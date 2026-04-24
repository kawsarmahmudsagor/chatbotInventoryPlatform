from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from modules.llms.schemas.llm_schema import LLMCreate, LLMRead, LLMUpdate
from modules.llms.services import llm_service
from modules.vendors.models.vendor_model import Vendor
from modules.auth.vendors import auth_vendor

router = APIRouter(tags=["LLMs"])


@router.post("/", response_model=LLMRead)
def create_llm(
    data: LLMCreate,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    return llm_service.create_llm(db, data, vendor_id=current_vendor.id)


@router.get("/", response_model=List[LLMRead])
def list_llms(
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    return llm_service.get_llms(db, vendor_id=current_vendor.id)


@router.get("/{llm_id}", response_model=LLMRead)
def get_llm(
    llm_id: int,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    llm = llm_service.get_llm(db, llm_id, vendor_id=current_vendor.id)
    if not llm:
        raise HTTPException(status_code=404, detail="LLM not found")
    return llm


@router.put("/{llm_id}", response_model=LLMRead)
def update_llm(
    llm_id: int,
    llm_data: LLMUpdate,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    llm = llm_service.update_llm(db, llm_id, llm_data, vendor_id=current_vendor.id)
    if not llm:
        raise HTTPException(status_code=404, detail="LLM not found")
    return llm


@router.delete("/{llm_id}")
def delete_llm(
    llm_id: int,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    success = llm_service.delete_llm(db, llm_id, vendor_id=current_vendor.id)
    if not success:
        raise HTTPException(status_code=404, detail="LLM not found")
    return {"detail": "LLM deleted successfully"}