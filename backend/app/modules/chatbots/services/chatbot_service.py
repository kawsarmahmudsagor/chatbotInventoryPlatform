from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Optional
from uuid import uuid4
from core.enums import SenderType, VectorStoreType, DocumentStatus
from modules.api_keys.models.api_model import APIKey
from modules.chatbots.models.chatbot_model import Chatbot
from modules.conversations.models.conversation_model import Conversation
from modules.embeddings.models.embedding_model import Embedding
from modules.vendors.models.vendor_model import Vendor
from modules.messages.models.messages_model import Message
from modules.rag.services import rag_service
from modules.users.models.user_model import User
from modules.api_keys.models.api_model import APIKey
from modules.chatbots.services import chatbot_service
from modules.chatbots.models.chatbot_model import Chatbot
from modules.chatbots.schemas.chatbot_schema import ChatbotCreate, ChatbotUpdate


def create_chatbot(db: Session, chatbot_data: ChatbotCreate) -> Chatbot:
    chatbot = Chatbot(**chatbot_data.dict())
    db.add(chatbot)
    db.commit()
    db.refresh(chatbot)
    return chatbot


def update_chatbot(
    db: Session, chatbot_id: int, chatbot_data: ChatbotUpdate
) -> Optional[Chatbot]:
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        return None

    if chatbot_data.name        is not None: chatbot.name        = chatbot_data.name
    if chatbot_data.vendor_id   is not None: chatbot.vendor_id   = chatbot_data.vendor_id
    if chatbot_data.description is not None: chatbot.description = chatbot_data.description
    if chatbot_data.llm_id      is not None: chatbot.llm_id      = chatbot_data.llm_id
    if chatbot_data.llm_path    is not None: chatbot.llm_path    = chatbot_data.llm_path
    if chatbot_data.is_active   is not None: chatbot.is_active   = chatbot_data.is_active

    db.commit()
    db.refresh(chatbot)
    return chatbot


def get_chatbots(db: Session) -> List[Chatbot]:
    return db.query(Chatbot).all()

def get_role_based_stats(db: Session, chatbot_id: int):
    chatbot = (db.query(Chatbot)
        .options(joinedload(Chatbot.vendor), joinedload(Chatbot.llm))
        .filter(Chatbot.id == chatbot_id)
        .first()
    )

    if not chatbot:
        return None
    else :
        return chatbot
    

def count_of_chatbots(db : Session) -> int:
    return db.query(func.count(Chatbot.id)).scalar()

def top_performing_chatbot_name(db: Session) -> str | None:
    result = (
        db.query(
            Chatbot.name
        )
        .join(Conversation, Conversation.chatbot_id == Chatbot.id)
        .group_by(Chatbot.id)
        .order_by(
            (
                func.count(Conversation.id) /
                func.count(func.distinct(Conversation.session_id))
            ).desc()
        )
        .first()
    )

    return result[0] if result else None

def get_vendor_chatbots(db: Session, vendor_id: int) -> List[Chatbot]:
    return db.query(Chatbot).filter(Chatbot.vendor_id == vendor_id).all()

def get_chatbot(db: Session, chatbot_id: int) -> Chatbot:
    return db.query(Chatbot).get(chatbot_id)

def duplicate_chatbot(db: Session, chatbot_id: int):
    chatbot = db.query(Chatbot).get(chatbot_id)
    if not chatbot:
        return None
    data = {c.name: getattr(chatbot, c.name) for c in Chatbot.__table__.columns if c.name != "id"}
    new_chatbot = Chatbot(**data)
    db.add(new_chatbot)
    db.commit()
    db.refresh(new_chatbot)
    return new_chatbot


def delete_chatbot(db: Session, chatbot_id: int) -> bool:
    chatbot = db.query(Chatbot).get(chatbot_id)
    if not chatbot:
        return False
    db.delete(chatbot)
    db.commit()
    return True

def handle_conversation_singleturn(
    db: Session,
    question: str,
    chatbot_id: int,
    token: str
):
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.is_active == True
    ).first()

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found or inactive")

    api_token = db.query(APIKey).filter(APIKey.token_hash==token, APIKey.chatbot_id==chatbot.id).first()
    if not api_token:
        raise HTTPException(status_code=404, detail="API Key not found or incorrect")    

    llm_obj = chatbot.llm
    if not llm_obj:
        raise HTTPException(status_code=404, detail="LLM not found for this chatbot")

    if not chatbot.llm_path:
        raise HTTPException(status_code=400, detail="Chatbot does not have an LLM path configured")

    if not chatbot.llm_path or chatbot.llm_path.strip() == "":
        raise HTTPException(status_code=400, detail="Chatbot llm_path is empty or not configured")

    model = ChatOllama(
        model=chatbot.llm_path.strip(),
        temperature=0.7,
    )

    vector_db_obj = chatbot_service.get_latest_vector_db(chatbot)

    embedd_obj = db.query(Embedding).filter(
        Embedding.id == llm_obj.embedding_id
    ).first()

    if not embedd_obj:
        raise HTTPException(status_code=404, detail="Embedding not found for this LLM")

    embeddings = OllamaEmbeddings(model=embedd_obj.model_name)

    if vector_db_obj:
        vectordb = rag_service.load_vectorstore(
            chatbot.vector_store_type,
            vector_db_obj.db_path,
            embeddings
        )
        context, _ = rag_service.get_rag_context(question, vectordb)
    else:
        context = None
    
    system_msg = SystemMessage(
        content=chatbot.system_prompt or "You are a helpful assistant."
    )

    final_question = (
        f"Context:\n{context}\n\nQuestion:\n{question}"
        if context else question
    )

    human_msg = HumanMessage(content=final_question)
    response = model.invoke([system_msg, human_msg])
    return response.content

def handle_conversation_multiturn(
    db: Session,
    question: str,
    chatbot_id: int,
    session_id: str,
    token: str,
    user: User | None = None
):

    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.is_active == True
    ).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found or inactive")
    
    api_token = db.query(APIKey).filter(APIKey.token_hash==token, APIKey.chatbot_id==chatbot.id).first()
    if not api_token:
        raise HTTPException(status_code=404, detail="API Key not found or incorrect")

    llm_obj = chatbot.llm
    if not llm_obj:
        raise HTTPException(status_code=404, detail="LLM not found for this chatbot")

    if not chatbot.llm_path or not chatbot.llm_path.strip():
        raise HTTPException(status_code=400, detail="Chatbot LLM path not configured")

    # --- Fetch or create conversation ---
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.session_id == session_id,
            Conversation.chatbot_id == chatbot_id
        )
        .first()
    )

    if conversation is None:
        conversation = Conversation(
            session_id=session_id,
            chatbot_id=chatbot_id,
            user_id=user.id if user else None,
            is_active=True  # mark new conversation as active
        )
        db.add(conversation)
        try:
            db.commit()
            db.refresh(conversation)
        except IntegrityError:
            db.rollback()
            conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.session_id == session_id,
                    Conversation.chatbot_id == chatbot_id
                )
                .first()
            )
            if conversation is None:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create or fetch conversation"
                )
            db.refresh(conversation)

    # --- Check for "bye" message ---
    if question.strip().lower() in ("bye", "goodbye", "see you"):
        conversation.is_active = False
        db.commit()
        return "It was nice chatting with you. Goodbye!"

    # --- Fetch conversation history only if active ---
    history = []
    if conversation.is_active:
        history = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
            .all()
        )

    messages = [
        SystemMessage(content=chatbot.system_prompt or "You are a helpful assistant.")
    ]

    for msg in history:
        if msg.sender_type in (SenderType.external, SenderType.vendor, SenderType.admin):
            messages.append(HumanMessage(content=msg.content))
        else:  # chatbot messages
            messages.append(AIMessage(content=msg.content))

    # --- Prepare embeddings and context if RAG is used ---
    embedd_obj = db.query(Embedding).filter(Embedding.id == llm_obj.embedding_id).first()
    embeddings = OllamaEmbeddings(model=embedd_obj.model_name) if embedd_obj else None

    vector_db_obj = chatbot_service.get_latest_vector_db(chatbot)
    if vector_db_obj and embeddings:
        vectordb = rag_service.load_vectorstore(
            chatbot.vector_store_type,
            vector_db_obj.db_path,
            embeddings
        )
        context, _ = rag_service.get_rag_context(question, vectordb)
    else:
        context = None

    final_question = (
        f"Context:\n{context}\n\nQuestion:\n{question}"
        if context else question
    )
    messages.append(HumanMessage(content=final_question))

    # --- Call the LLM ---
    model = ChatOllama(model=chatbot.llm_path.strip(), temperature=0.6)
    response = model.invoke(messages)
    ai_text = response.content

    # --- Save user message ---
    db.add(Message(
        conversation_id=conversation.id,
        sender_type=SenderType.external if not user else SenderType(user.role.value),
        content=question,
        token_count=len(question.split())
    ))

    # --- Save bot message ---
    db.add(Message(
        conversation_id=conversation.id,
        sender_type=SenderType.chatbot,
        content=ai_text,
        token_count=len(ai_text.split())
    ))

    db.commit()

    return ai_text

def test_handle_conversation_multiturn(
    db: Session,
    question: str,
    chatbot_id: int,
    session_id: str,
    user: User | None = None
):

    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.is_active == True
    ).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found or inactive")

    llm_obj = chatbot.llm
    if not llm_obj:
        raise HTTPException(status_code=404, detail="LLM not found for this chatbot")

    if not chatbot.llm_path or not chatbot.llm_path.strip():
        raise HTTPException(status_code=400, detail="Chatbot LLM path not configured")

    # --- Fetch or create conversation ---
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.session_id == session_id,
            Conversation.chatbot_id == chatbot_id
        )
        .first()
    )

    if conversation is None:
        conversation = Conversation(
            session_id=session_id,
            chatbot_id=chatbot_id,
            user_id=user.id if user else None,
            is_active=True  # mark new conversation as active
        )
        db.add(conversation)
        try:
            db.commit()
            db.refresh(conversation)
        except IntegrityError:
            db.rollback()
            conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.session_id == session_id,
                    Conversation.chatbot_id == chatbot_id
                )
                .first()
            )
            if conversation is None:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create or fetch conversation"
                )
            db.refresh(conversation)

    # --- Check for "bye" message ---
    if question.strip().lower() in ("bye", "goodbye", "see you"):
        conversation.is_active = False
        db.commit()
        return "It was nice chatting with you. Goodbye!"

    # --- Fetch conversation history only if active ---
    history = []
    if conversation.is_active:
        history = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
            .all()
        )

    messages = [
        SystemMessage(content=chatbot.system_prompt or "You are a helpful assistant.")
    ]

    for msg in history:
        if msg.sender_type in (SenderType.external, SenderType.vendor, SenderType.admin):
            messages.append(HumanMessage(content=msg.content))
        else:  # chatbot messages
            messages.append(AIMessage(content=msg.content))

    # --- Prepare embeddings and context if RAG is used ---
    embedd_obj = db.query(Embedding).filter(Embedding.id == llm_obj.embedding_id).first()
    embeddings = OllamaEmbeddings(model=embedd_obj.model_name) if embedd_obj else None

    vector_db_obj = chatbot_service.get_latest_vector_db(chatbot)
    if vector_db_obj and embeddings:
        vectordb = rag_service.load_vectorstore(
            chatbot.vector_store_type,
            vector_db_obj.db_path,
            embeddings
        )
        context, _ = rag_service.get_rag_context(question, vectordb)
    else:
        context = None

    final_question = (
        f"Context:\n{context}\n\nQuestion:\n{question}"
        if context else question
    )
    messages.append(HumanMessage(content=final_question))

    # --- Call the LLM ---
    model = ChatOllama(model=chatbot.llm_path.strip(), temperature=0.6)
    response = model.invoke(messages)
    ai_text = response.content

    # --- Save user message ---
    db.add(Message(
        conversation_id=conversation.id,
        sender_type=SenderType.external if not user else SenderType(user.role.value),
        content=question,
        token_count=len(question.split())
    ))

    # --- Save bot message ---
    db.add(Message(
        conversation_id=conversation.id,
        sender_type=SenderType.chatbot,
        content=ai_text,
        token_count=len(ai_text.split())
    ))

    db.commit()

    return ai_text


#  GLOBAL TOP CHATBOTS (Public Analytics)
def get_global_top_chatbots(db: Session, limit: int = 3):

    rows = (
        db.query(
            Chatbot.id.label("chatbot_id"),
            Chatbot.name.label("chatbot_name"),
            Vendor.id.label("vendor_id"),
            Vendor.name.label("vendor_name"),
            func.count(Conversation.id).label("message_count")
        )
        .join(Vendor, Vendor.id == Chatbot.vendor_id)
        .join(Conversation, Conversation.chatbot_id == Chatbot.id)
        .group_by(Chatbot.id, Vendor.id)
        .order_by(func.count(Conversation.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "chatbot_id": r.chatbot_id,
            "chatbot_name": r.chatbot_name,
            "vendor_id": r.vendor_id,
            "vendor_name": r.vendor_name
        }
        for r in rows
    ]