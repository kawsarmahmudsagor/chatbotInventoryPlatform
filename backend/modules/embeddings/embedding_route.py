from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.database import get_db
from chatbot.chatbotInventoryPlatform.backend.modules.llms.llm_schema import EmbeddingCreate, EmbeddingRead
from chatbot.chatbotInventoryPlatform.backend.modules.llms import operations as llm_ops

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])

@router.post("/", response_model=EmbeddingRead)
def create_embedding(embed: EmbeddingCreate, db: Session = Depends(get_db)):
    return llm_ops.create_embedding(db, embed)

@router.get("/", response_model=List[EmbeddingRead])
def get_embeddings(db: Session = Depends(get_db)):
    return llm_ops.get_embeddings(db)

@router.get("/{embedding_id}", response_model=EmbeddingRead)
def get_embedding(embedding_id: int, db: Session = Depends(get_db)):
    embed = llm_ops.get_embedding(db, embedding_id)
    if not embed:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return embed

@router.put("/{embedding_id}", response_model=EmbeddingRead)
def update_embedding(embedding_id: int, embed_data: EmbeddingCreate, db: Session = Depends(get_db)):
    embed = llm_ops.update_embedding(db, embedding_id, embed_data)
    if not embed:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return embed

@router.delete("/{embedding_id}")
def delete_embedding(embedding_id: int, db: Session = Depends(get_db)):
    success = llm_ops.delete_embedding(db, embedding_id)
    if not success:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return {"detail": "Embedding deleted successfully"}
