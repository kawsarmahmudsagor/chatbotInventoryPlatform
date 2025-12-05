from pydantic import BaseModel
from typing import Optional
from chatbot.chatbotInventoryPlatform.backend.core.enums import ChatbotMode

class ChatbotBase(BaseModel):
    vendor_id: int
    name: str
    description: Optional[str] = None
    system_prompt: str
    llm_id: Optional[int] = None
    vector_db: str
    mode: ChatbotMode = ChatbotMode.private
    is_active: bool = True
    token_limit: int
    context_limit: int

class ChatbotCreate(ChatbotBase):
    pass

class ChatbotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    llm_id: Optional[int] = None
    vector_db: Optional[str] = None
    mode: Optional[ChatbotMode] = None
    is_active: Optional[bool] = None
    token_limit: Optional[int] = None
    context_limit: Optional[int] = None

class ChatbotRead(ChatbotBase):
    id: int

    class Config:
        orm_mode = True

