from sqlalchemy.orm import Session
from typing import List
from chatbot.chatbotInventoryPlatform.backend.modules.llms.llm_model import LLM
from chatbot.chatbotInventoryPlatform.backend.modules.llms.llm_schema import LLMCreate

# -------------------------
# LLM CRUD
# -------------------------

def create_llm(db: Session, llm_data: LLMCreate) -> LLM:
    new_llm = LLM(**llm_data.dict())
    db.add(new_llm)
    db.commit()
    db.refresh(new_llm)
    return new_llm

def get_llms(db: Session) -> List[LLM]:
    return db.query(LLM).all()

def get_llm(db: Session, llm_id: int) -> LLM:
    return db.query(LLM).filter(LLM.id == llm_id).first()

def update_llm(db: Session, llm_id: int, llm_data: LLMCreate) -> LLM:
    llm = db.query(LLM).filter(LLM.id == llm_id).first()
    if not llm:
        return None
    for key, value in llm_data.dict().items():
        setattr(llm, key, value)
    db.commit()
    db.refresh(llm)
    return llm

def delete_llm(db: Session, llm_id: int) -> bool:
    llm = db.query(LLM).filter(LLM.id == llm_id).first()
    if not llm:
        return False
    db.delete(llm)
    db.commit()
    return True
