from sqlalchemy.orm import Session
from typing import List
from chatbot.chatbotInventoryPlatform.backend.modules.llms.llm_model import Embedding
from chatbot.chatbotInventoryPlatform.backend.modules.llms.llm_schema import EmbeddingCreate

# -------------------------
# Embedding CRUD
# -------------------------

def create_embedding(db: Session, embed_data: EmbeddingCreate) -> Embedding:
    new_embed = Embedding(**embed_data.dict())
    db.add(new_embed)
    db.commit()
    db.refresh(new_embed)
    return new_embed

def get_embeddings(db: Session) -> List[Embedding]:
    return db.query(Embedding).all()

def get_embedding(db: Session, embedding_id: int) -> Embedding:
    return db.query(Embedding).filter(Embedding.id == embedding_id).first()

def update_embedding(db: Session, embedding_id: int, embed_data: EmbeddingCreate) -> Embedding:
    embed = db.query(Embedding).filter(Embedding.id == embedding_id).first()
    if not embed:
        return None
    for key, value in embed_data.dict().items():
        setattr(embed, key, value)
    db.commit()
    db.refresh(embed)
    return embed

def delete_embedding(db: Session, embedding_id: int) -> bool:
    embed = db.query(Embedding).filter(Embedding.id == embedding_id).first()
    if not embed:
        return False
    db.delete(embed)
    db.commit()
    return True
