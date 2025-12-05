from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from chatbot.chatbotInventoryPlatform.backend.core.enums import SenderType

class ConversationBase(BaseModel):
    session_id: str
    sender_type: SenderType
    content: str
    user_id: Optional[int] = None
    chatbot_id: Optional[int] = None
    token_count: int = 0

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    content: Optional[str] = None
    token_count: Optional[int] = None

class ConversationRead(ConversationBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

