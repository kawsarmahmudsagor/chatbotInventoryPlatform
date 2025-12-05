from pydantic import BaseModel
from typing import Optional

class EmbeddingBase(BaseModel):
    name: str
    model_name: str

class EmbeddingCreate(EmbeddingBase):
    pass

class EmbeddingUpdate(BaseModel):
    name: Optional[str] = None
    model_name: Optional[str] = None

class EmbeddingRead(EmbeddingBase):
    id: int

    class Config:
        orm_mode = True
