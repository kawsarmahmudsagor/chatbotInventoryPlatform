from pydantic import BaseModel
from typing import List

class EmbeddingModelBase(BaseModel):
    name: str

class EmbeddingModelCreate(EmbeddingModelBase):
    pass

class EmbeddingModelRead(EmbeddingModelBase):
    id: int

    class Config:
        orm_mode = True
