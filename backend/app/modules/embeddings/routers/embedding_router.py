from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from modules.embeddings.schemas.embedding_schema import EmbeddingCreate, EmbeddingRead, EmbeddingUpdate
from modules.embeddings.services import embedding_service
from modules.vendors.models.vendor_model import Vendor
from modules.auth.vendors import auth_vendor

router = APIRouter(tags=["Embeddings"])


@router.post("/create", response_model=EmbeddingRead)
def add_embedding(
    data: EmbeddingCreate,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    return embedding_service.add_embedding(db, data, vendor_id=current_vendor.id)


@router.get("/", response_model=List[EmbeddingRead])
def get_embeddings(
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    return embedding_service.get_embeddings(db, vendor_id=current_vendor.id)


@router.get("/{embedding_id}", response_model=EmbeddingRead)
def get_embedding(
    embedding_id: int,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    embed = embedding_service.get_embedding(db, embedding_id, vendor_id=current_vendor.id)
    if not embed:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return embed


@router.put("/update/{embedding_id}", response_model=EmbeddingRead)
def update_embedding(
    embedding_id: int,
    embed_data: EmbeddingUpdate,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    embed = embedding_service.update_embedding(db, embedding_id, embed_data, vendor_id=current_vendor.id)
    if not embed:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return embed


@router.delete("/delete/{embedding_id}")
def delete_embedding(
    embedding_id: int,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    success = embedding_service.delete_embedding(db, embedding_id, vendor_id=current_vendor.id)
    if not success:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return {"detail": "Embedding deleted successfully"}