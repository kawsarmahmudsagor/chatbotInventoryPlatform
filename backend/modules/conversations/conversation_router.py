from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.database import get_db
from chatbot.chatbotInventoryPlatform.backend.modules.conversations.conversation_schema import ConversationCreate, ConversationRead
from chatbot.chatbotInventoryPlatform.backend.modules.conversations import operations

router = APIRouter(prefix="/conversations", tags=["Conversations"])

# --- Conversations CRUD ---
@router.post("/", response_model=ConversationRead)
def create_conversation(conv: ConversationCreate, db: Session = Depends(get_db)):
    return operations.create_conversation(db, conv)

@router.get("/", response_model=List[ConversationRead])
def get_conversations(db: Session = Depends(get_db)):
    return operations.get_conversations(db)

@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = operations.get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.put("/{conversation_id}", response_model=ConversationRead)
def update_conversation(conversation_id: int, conv_data: ConversationCreate, db: Session = Depends(get_db)):
    conv = operations.update_conversation(db, conversation_id, conv_data)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    success = operations.delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"detail": "Conversation deleted successfully"}
