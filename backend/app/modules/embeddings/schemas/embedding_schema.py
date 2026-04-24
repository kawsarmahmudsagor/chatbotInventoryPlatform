from pydantic import BaseModel, ConfigDict
from typing import Optional
from core.enums import EmbeddingProvider

class EmbeddingBase(BaseModel):
    model_name: str
    provider:   EmbeddingProvider
    path:       Optional[str] = None

class EmbeddingCreate(EmbeddingBase):
    pass  # vendor_id injected from auth in router, not from request body

class EmbeddingUpdate(BaseModel):
    model_name: Optional[str]             = None
    provider:   Optional[EmbeddingProvider] = None
    path:       Optional[str]             = None

class EmbeddingRead(EmbeddingBase):
    id:        int
    vendor_id: int

    model_config = ConfigDict(from_attributes=True)