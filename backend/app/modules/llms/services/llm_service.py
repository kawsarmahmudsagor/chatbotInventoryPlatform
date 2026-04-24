from sqlalchemy.orm import Session
import threading, subprocess
from typing import List, Optional
from modules.llms.models.llm_model import LLM
from modules.llms.schemas.llm_schema import LLMCreate, LLMUpdate


def create_llm(db: Session, data: LLMCreate, vendor_id: int) -> LLM:
    llm = LLM(**data.dict(), vendor_id=vendor_id)
    db.add(llm)
    db.commit()
    db.refresh(llm)
    if llm.path:
        pull_in_background(llm.path)
    return llm


def pull_in_background(path: str):
    threading.Thread(
        target=lambda: subprocess.call(["ollama", "pull", path]),
        daemon=True
    ).start()


def get_llms(db: Session, vendor_id: int) -> List[LLM]:
    return db.query(LLM).filter(LLM.vendor_id == vendor_id).all()


def get_llm(db: Session, llm_id: int, vendor_id: int) -> Optional[LLM]:
    return db.query(LLM).filter(
        LLM.id == llm_id,
        LLM.vendor_id == vendor_id
    ).first()


def update_llm(db: Session, llm_id: int, llm_data: LLMUpdate, vendor_id: int) -> Optional[LLM]:
    llm = db.query(LLM).filter(
        LLM.id == llm_id,
        LLM.vendor_id == vendor_id
    ).first()
    if not llm:
        return None
    for key, value in llm_data.dict(exclude_unset=True).items():
        setattr(llm, key, value)
    db.commit()
    db.refresh(llm)
    return llm


def delete_llm(db: Session, llm_id: int, vendor_id: int) -> bool:
    llm = db.query(LLM).filter(
        LLM.id == llm_id,
        LLM.vendor_id == vendor_id
    ).first()
    if not llm:
        return False
    db.delete(llm)
    db.commit()
    return True