from sqlalchemy.orm import Session
from typing import List
from chatbot.chatbotInventoryPlatform.backend.modules.conversations.conversation_model import Conversation
from chatbot.chatbotInventoryPlatform.backend.modules.conversations.conversation_schema import ConversationCreate

# -------------------------
# Conversation CRUD
# -------------------------

def create_conversation(db: Session, conv_data: ConversationCreate) -> Conversation:
    new_conv = Conversation(**conv_data.dict())
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv

def get_conversations(db: Session) -> List[Conversation]:
    return db.query(Conversation).all()

def get_conversation(db: Session, conversation_id: int) -> Conversation:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def update_conversation(db: Session, conversation_id: int, conv_data: ConversationCreate) -> Conversation:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        return None
    for key, value in conv_data.dict().items():
        setattr(conv, key, value)
    db.commit()
    db.refresh(conv)
    return conv

def delete_conversation(db: Session, conversation_id: int) -> bool:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        return False
    db.delete(conv)
    db.commit()
    return True
