from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.database import get_db
from chatbot.chatbotInventoryPlatform.backend.modules.chatbots.chatbot_schema import ChatbotCreate, ChatbotRead
from chatbot.chatbotInventoryPlatform.backend.modules.chatbots import chatbot_service, chatmodel

router = APIRouter(prefix="/chatbots", tags=["Chatbots"])

@router.post("/", response_model=ChatbotRead)
def create_chatbot(chatbot: ChatbotCreate, db: Session = Depends(get_db)):
    return chatbot_service.create_chatbot(db, chatbot)

@router.get("/", response_model=List[ChatbotRead])
def get_chatbots(db: Session = Depends(get_db)):
    return chatbot_service.get_chatbots(db)

@router.get("/{chatbot_id}", response_model=ChatbotRead)
def get_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    chatbot = chatbot_service.get_chatbot(db, chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return chatbot

@router.put("/{chatbot_id}", response_model=ChatbotRead)
def update_chatbot(chatbot_id: int, chatbot_data: ChatbotCreate, db: Session = Depends(get_db)):
    chatbot = chatbot_service.update_chatbot(db, chatbot_id, chatbot_data)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return chatbot

@router.delete("/{chatbot_id}")
def delete_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    success = chatbot_service.delete_chatbot(db, chatbot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return {"detail": "Chatbot deleted successfully"}

@router.post("/{chatbot_id}/ask")
def chatbot_interaction_user_singleturn(
    chatbot_id: int,
    request: chatmodel.ChatRequest,
    db: Session = Depends(get_db),
    ):
    
    ai_reply= chatbot_service.handle_conversation_singleturn(db, request.message, chatbot_id)

    return {
        "response": ai_reply
    }
