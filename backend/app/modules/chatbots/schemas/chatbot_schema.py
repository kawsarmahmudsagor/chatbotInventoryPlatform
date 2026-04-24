from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from modules.vendors.schemas.vendor_schema import VendorRead
from modules.llms.schemas.llm_schema import LLMRead

class ChatbotBase(BaseModel):
    vendor_id:   int
    name:        str
    description: Optional[str] = None
    llm_id:      Optional[int] = None
    llm_path:    Optional[str] = None
    is_active:   bool = True

class ChatbotCreate(ChatbotBase):
    pass

class ChatbotUpdate(BaseModel):
    name:        Optional[str]  = None
    vendor_id:   Optional[int]  = None
    description: Optional[str]  = None
    llm_id:      Optional[int]  = None
    llm_path:    Optional[str]  = None
    is_active:   Optional[bool] = None

class ChatbotRead(ChatbotBase):
    id:         int
    vendor:     Optional[VendorRead] = None
    llm:        Optional[LLMRead]    = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatbotVendorRead(BaseModel):
    id:          int
    name:        str
    description: Optional[str] = None
    is_active:   bool
    created_at:  datetime

    model_config = ConfigDict(from_attributes=True)