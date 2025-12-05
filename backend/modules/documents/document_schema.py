from pydantic import BaseModel
from typing import Optional
from chatbot.chatbotInventoryPlatform.backend.core.enums import DocumentStatus

class DocumentBase(BaseModel):
    vendor_id: int
    chatbot_id: int
    title: str
    summary: str
    tags: str
    file_path: str
    status: DocumentStatus = DocumentStatus.processing

class DocumentCreate(BaseModel):
    title: str
    tags: str
    file_path: str
    summary: Optional[str] = ""   # can be populated after ingestion
    status: DocumentStatus = DocumentStatus.processing

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[DocumentStatus] = None

class DocumentRead(DocumentBase):
    id: int

    class Config:
        orm_mode = True

