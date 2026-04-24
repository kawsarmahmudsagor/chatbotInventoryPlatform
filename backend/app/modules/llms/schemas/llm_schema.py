from pydantic import BaseModel, ConfigDict
from typing import Optional
from modules.embeddings.schemas.embedding_schema import EmbeddingRead

class LLMBase(BaseModel):
    name:              str
    provider:          str
    embedding_id:      int
    def_token_limit:   int
    def_context_limit: int
    path:              Optional[str] = None

class LLMCreate(LLMBase):
    pass  # vendor_id injected from auth in router

class LLMUpdate(BaseModel):
    name:              Optional[str] = None
    provider:          Optional[str] = None
    embedding_id:      Optional[int] = None
    def_token_limit:   Optional[int] = None
    def_context_limit: Optional[int] = None
    path:              Optional[str] = None

class LLMRead(LLMBase):
    id:        int
    vendor_id: int
    embedding: Optional[EmbeddingRead] = None

    model_config = ConfigDict(from_attributes=True)