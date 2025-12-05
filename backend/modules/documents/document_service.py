from sqlalchemy.orm import Session
from typing import List
from chatbot.chatbotInventoryPlatform.backend.modules.documents.document_model import Document
from chatbot.chatbotInventoryPlatform.backend.modules.documents.document_schema import DocumentCreate

# -------------------------
# Document CRUD
# -------------------------

def create_document(db: Session, document_data: DocumentCreate) -> Document:
    new_doc = Document(**document_data.dict())
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

def get_documents(db: Session) -> List[Document]:
    return db.query(Document).all()

def get_document(db: Session, document_id: int) -> Document:
    return db.query(Document).filter(Document.id == document_id).first()

def update_document(db: Session, document_id: int, document_data: DocumentCreate) -> Document:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return None
    for key, value in document_data.dict().items():
        setattr(document, key, value)
    db.commit()
    db.refresh(document)
    return document

def delete_document(db: Session, document_id: int) -> bool:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return False
    db.delete(document)
    db.commit()
    return True
