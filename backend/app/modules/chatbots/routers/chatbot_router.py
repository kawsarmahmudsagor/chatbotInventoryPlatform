from fastapi import APIRouter, Depends, HTTPException,UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import uuid4
from db.database import get_db
from modules.chatbots.schemas.chatbot_schema import ChatbotCreate, ChatbotRead, ChatbotUpdate, ChatbotVendorRead
from modules.chatbots.services import chatbot_service
from modules.chatbots.models.chatmodel import ChatRequest, ChatResponse
from modules.vendors.models.vendor_model import Vendor
from modules.admins.models.admin_model import Admin
from modules.users.models.user_model import User
from modules.chatbots.models.chatbot_model import Chatbot
from modules.api_keys.models.api_model import APIKey
from core.enums import VectorStoreType, UserRole
from modules.auth.vendors.auth_vendor import get_current_vendor
from modules.auth.admins.auth_admin import get_current_admin
from modules.auth.users.auth_user import get_current_user, get_current_user_optional


router = APIRouter(tags=["Chatbots"])

@router.post("/create", response_model=ChatbotRead)
def create_chatbot(
    vendor_id:   int            = Form(...),
    name:        str            = Form(...),
    description: Optional[str] = Form(None),
    llm_id:      int            = Form(...),
    llm_path:    str            = Form(...),
    is_active:   bool           = Form(True),
    db:          Session        = Depends(get_db),
):
    data = ChatbotCreate(
        vendor_id=vendor_id,
        name=name,
        description=description or "",
        llm_id=llm_id,
        llm_path=llm_path,
        is_active=is_active,
    )
    return chatbot_service.create_chatbot(db, data)


@router.put("/{chatbot_id}", response_model=ChatbotRead)
def update_chatbot(
    chatbot_id:  int,
    name:        Optional[str]  = Form(None),
    vendor_id:   Optional[int]  = Form(None),
    description: Optional[str]  = Form(None),
    llm_id:      Optional[int]  = Form(None),
    llm_path:    Optional[str]  = Form(None),
    is_active:   Optional[bool] = Form(None),
    db:          Session        = Depends(get_db),
):
    data = ChatbotUpdate(
        name=name, vendor_id=vendor_id, description=description,
        llm_id=llm_id, llm_path=llm_path, is_active=is_active,
    )
    chatbot = chatbot_service.update_chatbot(db, chatbot_id, data)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return chatbot


@router.get("/{chatbot_id}", response_model=ChatbotRead)
def get_chatbot(
    chatbot_id: int,
    db: Session = Depends(get_db),
):
    chatbot = chatbot_service.get_chatbot(db, chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return chatbot

@router.delete("/{chatbot_id}")
def delete_chatbot(
    chatbot_id: int,
    db: Session = Depends(get_db),
):
    if not chatbot_service.delete_chatbot(db, chatbot_id):
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return {"message": "Chatbot deleted"}

@router.get("/", response_model=List[ChatbotRead])
def get_vendor_chatbots(db: Session = Depends(get_db),  current_vendor: Vendor = Depends(get_current_vendor)):
    return chatbot_service.get_vendor_chatbots(db, current_vendor.id)

@router.get("/vendor_chatbots_for_user/{vendor_id}", response_model=List[ChatbotRead])
def get_vendor_chatbots_for_users(vendor_id: int, db: Session = Depends(get_db)):
    return chatbot_service.get_vendor_chatbots(db, vendor_id)


@router.get("/", response_model=List[ChatbotRead])
def get_chatbots(db: Session = Depends(get_db)):
    return chatbot_service.get_chatbots(db)

@router.get("/{chatbot_id}", response_model=ChatbotRead)
def get_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    chatbot = chatbot_service.get_chatbot(db, chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return chatbot

@router.get("/role-based-stats/{chatbot_id}/{user_role}")
def role_based_stats(chatbot_id: int, user_role: UserRole, db: Session = Depends(get_db)):
    chatbot = chatbot_service.get_role_based_stats(db, chatbot_id)

    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    if user_role == UserRole.admin:
        return ChatbotRead.from_orm(chatbot)
    elif user_role == UserRole.vendor:
        return ChatbotVendorRead.from_orm(chatbot)
    else:
        raise HTTPException(status_code=403, detail="User role not allowed")


@router.post("/{token}/ask", response_model=ChatResponse)
def chatbot_interaction_user_singleturn(
    token: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    api_key = db.query(APIKey).filter(APIKey.token_hash == token, APIKey.status == "active").first()
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    chatbot = db.query(Chatbot).filter(Chatbot.id == api_key.chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    ai_reply = chatbot_service.handle_conversation_singleturn(
        db=db,
        question=request.question,
        chatbot_id=chatbot.id,
        token=token
    )
    return ChatResponse(
    answer=ai_reply.content if hasattr(ai_reply, "content") else str(ai_reply),
    session_id=None
    )

@router.post("/{token}/chat", response_model=ChatResponse)
def chatbot_interaction_multiturn(
    token: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional), 
):
    api_key = db.query(APIKey).filter(APIKey.token_hash == token, APIKey.status == "active").first()
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    chatbot = db.query(Chatbot).filter(Chatbot.id == api_key.chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    session_id = request.session_id or str(uuid4())

    ai_text = chatbot_service.handle_conversation_multiturn(
        db=db,
        question=request.question,
        chatbot_id=chatbot.id,
        session_id=session_id,
        user=current_user, 
        token=token 
    )

    return ChatResponse(
        answer=ai_text,
        session_id=session_id
    )

@router.post("/test/{chatbot_id}/chat", response_model=ChatResponse)
def test_chatbot_interaction_multiturn(
    chatbot_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional), 
):
    session_id = request.session_id or str(uuid4())

    ai_text = chatbot_service.test_handle_conversation_multiturn(
        db=db,
        question=request.question,
        chatbot_id=chatbot_id,
        session_id=session_id,
        user=current_user,  
    )

    return ChatResponse(
        answer=ai_text,
        session_id=session_id
    )

#  GLOBAL PUBLIC ANALYTICS
@router.get("/global/top-chatbots")
def global_top_chatbots(
    db: Session = Depends(get_db)
):
    return chatbot_service.get_global_top_chatbots(db)

