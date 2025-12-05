from FastAPI import HTTPException
from sqlalchemy.orm import Session
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from typing import List
from chatbot.chatbotInventoryPlatform.backend.modules.llms.llm_model import LLM
from chatbot.chatbotInventoryPlatform.backend.modules.chatbots.chatbot_model import Chatbot
from chatbot.chatbotInventoryPlatform.backend.modules.chatbots.chatbot_schema import ChatbotCreate

def create_chatbot(db: Session, chatbot_data: ChatbotCreate) -> Chatbot:
    new_chatbot = Chatbot(**chatbot_data.dict())
    db.add(new_chatbot)
    db.commit()
    db.refresh(new_chatbot)
    return new_chatbot

def get_chatbots(db: Session) -> List[Chatbot]:
    return db.query(Chatbot).all()

def get_chatbot(db: Session, chatbot_id: int) -> Chatbot:
    return db.query(Chatbot).get(chatbot_id)

def update_chatbot(db: Session, chatbot_id: int, chatbot_data: ChatbotCreate) -> Chatbot:
    chatbot = db.query(Chatbot).get(chatbot_id)
    if not chatbot:
        return None
    for key, value in chatbot_data.dict().items():
        setattr(chatbot, key, value)
    db.add(chatbot)
    db.commit()
    db.refresh(chatbot)
    return chatbot

def delete_chatbot(db: Session, chatbot_id: int) -> bool:
    chatbot = db.query(Chatbot).get(chatbot_id)
    if not chatbot:
        return False
    db.delete(chatbot)
    db.commit()
    return True

def handle_conversation_singleturn(db: Session, question, chatbot_id):
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id, Chatbot.is_active == True).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found or inactive")
    
    llm_obj = db.query(LLM).filter(LLM.id == chatbot.llm_id).first()
    if not llm_obj:
        raise HTTPException(status_code=404, detail="LLM not found for this chatbot")

    model_name = llm_obj.name
    model = init_chat_model(model_name)

    system_msg = SystemMessage(content=chatbot.system_prompt or "You are a helpful assistant.")
    human_msg = HumanMessage(content=question)

    messages = [system_msg, human_msg]

    response = model.invoke(messages)

    return response  
