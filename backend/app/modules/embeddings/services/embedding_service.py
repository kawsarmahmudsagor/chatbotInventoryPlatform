from sqlalchemy.orm import Session
import threading, subprocess
from typing import List, Optional
from modules.embeddings.models.embedding_model import Embedding
from modules.embeddings.schemas.embedding_schema import EmbeddingCreate, EmbeddingUpdate


def add_embedding(db: Session, embed_data: EmbeddingCreate, vendor_id: int) -> Embedding:
    new_embed = Embedding(**embed_data.dict(), vendor_id=vendor_id)
    db.add(new_embed)
    db.commit()
    db.refresh(new_embed)
    if new_embed.path:
        pull_in_background(new_embed.path)
    return new_embed


def pull_in_background(path: str):
    threading.Thread(
        target=lambda: subprocess.call(["ollama", "pull", path]),
        daemon=True
    ).start()


def get_embeddings(db: Session, vendor_id: int) -> List[Embedding]:
    return db.query(Embedding).filter(Embedding.vendor_id == vendor_id).all()


def get_embedding(db: Session, embedding_id: int, vendor_id: int) -> Optional[Embedding]:
    return db.query(Embedding).filter(
        Embedding.id == embedding_id,
        Embedding.vendor_id == vendor_id
    ).first()


def update_embedding(
    db: Session, embedding_id: int,
    embed_data: EmbeddingUpdate, vendor_id: int
) -> Optional[Embedding]:
    embed = db.query(Embedding).filter(
        Embedding.id == embedding_id,
        Embedding.vendor_id == vendor_id
    ).first()
    if not embed:
        return None
    for key, value in embed_data.dict(exclude_unset=True).items():
        setattr(embed, key, value)
    db.commit()
    db.refresh(embed)
    return embed


def delete_embedding(db: Session, embedding_id: int, vendor_id: int) -> bool:
    embed = db.query(Embedding).filter(
        Embedding.id == embedding_id,
        Embedding.vendor_id == vendor_id
    ).first()
    if not embed:
        return False
    db.delete(embed)
    db.commit()
    return True