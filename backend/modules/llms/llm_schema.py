from pydantic import BaseModel
from typing import Optional
from chatbot.chatbotInventoryPlatform.backend.schemas.embeddings import EmbeddingRead

class LLMBase(BaseModel):
    name: str
    embedding_id: int
    def_token_limit: int
    def_context_limit: int

class LLMCreate(LLMBase):
    pass

class LLMUpdate(BaseModel):
    name: Optional[str] = None
    embedding_id: Optional[int] = None
    def_token_limit: Optional[int] = None
    def_context_limit: Optional[int] = None

class LLMRead(LLMBase):
    id: int
    embedding: Optional[EmbeddingRead] = None  # nested read of embedding

    class Config:
        orm_mode = True

