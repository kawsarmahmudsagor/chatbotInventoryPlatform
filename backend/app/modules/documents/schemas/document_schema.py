from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from core.enums import DocumentStatus

class DocumentBase(BaseModel):
    agent_id:     int
    title:        str
    file_path:    str
    hash_address: Optional[str] = None   # NEW
    status:       DocumentStatus = DocumentStatus.processing

class DocumentCreate(BaseModel):
    title:        str
    file_path:    str
    hash_address: Optional[str] = None   # NEW
    status:       DocumentStatus = DocumentStatus.processing

class DocumentUpdate(BaseModel):
    title:        Optional[str]            = None
    hash_address: Optional[str]            = None   # NEW
    status:       Optional[DocumentStatus] = None

class DocumentRead(DocumentBase):
    id:         int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)