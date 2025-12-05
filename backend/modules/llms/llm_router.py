from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.database import get_db
from chatbot.chatbotInventoryPlatform.backend.modules.llms.llm_schema import LLMCreate, LLMRead
from chatbot.chatbotInventoryPlatform.backend.modules.llms import operations

router = APIRouter(prefix="/llms", tags=["LLMs"])

@router.post("/", response_model=LLMRead)
def create_llm(llm: LLMCreate, db: Session = Depends(get_db)):
    return operations.create_llm(db, llm)

@router.get("/", response_model=List[LLMRead])
def get_llms(db: Session = Depends(get_db)):
    return operations.get_llms(db)

@router.get("/{llm_id}", response_model=LLMRead)
def get_llm(llm_id: int, db: Session = Depends(get_db)):
    llm = operations.get_llm(db, llm_id)
    if not llm:
        raise HTTPException(status_code=404, detail="LLM not found")
    return llm

@router.put("/{llm_id}", response_model=LLMRead)
def update_llm(llm_id: int, llm_data: LLMCreate, db: Session = Depends(get_db)):
    llm = operations.update_llm(db, llm_id, llm_data)
    if not llm:
        raise HTTPException(status_code=404, detail="LLM not found")
    return llm

@router.delete("/{llm_id}")
def delete_llm(llm_id: int, db: Session = Depends(get_db)):
    success = operations.delete_llm(db, llm_id)
    if not success:
        raise HTTPException(status_code=404, detail="LLM not found")
    return {"detail": "LLM deleted successfully"}
