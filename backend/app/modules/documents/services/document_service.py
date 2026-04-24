from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from typing import List
from pathlib import Path
import uuid, shutil

from core.enums import DocumentStatus
from modules.documents.models.document_model import Document
from modules.documents.schemas.document_schema import DocumentCreate
from modules.rag.services import rag_service
from modules.agents.models.agent_model import Agent
from modules.chatbots.models.chatbot_model import Chatbot
from modules.llms.models.llm_model import LLM
from modules.embeddings.models.embedding_model import Embedding
from modules.vector_dbs.models.vector_db_model import VectorDB

PERMANENT_UPLOAD_DIR = Path("uploads/documents")
PERMANENT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def create_documents_bulk(
    db: Session,
    agent_id: int,          # CHANGED from chatbot_id
    files: List[UploadFile]
) -> List[Document]:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    upload_dir = PERMANENT_UPLOAD_DIR / str(agent_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_documents = []
    for file in files:
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = upload_dir / unique_filename

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        doc = Document(
            agent_id=agent_id,          # CHANGED
            title=file.filename,
            file_path=str(file_path),
            status=DocumentStatus.processing
        )
        db.add(doc)
        saved_documents.append(doc)

    db.commit()
    for doc in saved_documents:
        db.refresh(doc)

    return saved_documents


def embed_document(db: Session, document_id: int) -> VectorDB:
    try:
        document_obj = db.query(Document).filter(Document.id == document_id).first()
        if not document_obj:
            raise HTTPException(status_code=404, detail="Document not found")

        agent = db.query(Agent).filter(Agent.id == document_obj.agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")


        llm_obj = db.query(LLM).filter(LLM.id == agent.llm_id).first()
        if not llm_obj:
            raise HTTPException(status_code=404, detail="LLM not found")

        embedd_obj = db.query(Embedding).filter(Embedding.id == llm_obj.embedding_id).first()
        if not embedd_obj:
            raise HTTPException(status_code=404, detail="Embedding not found")

        document_list = db.query(Document).filter(Document.agent_id == agent.id).all()
        if not document_list:
            raise HTTPException(status_code=404, detail="No documents found")

        existing_vdb = db.query(VectorDB).filter(VectorDB.agent_id == agent.id).first()

        vectordb_obj, persist_path = rag_service.embedd_document(
            db, agent.id, embedd_obj, document_list
        )

        if vectordb_obj is None:
            if not existing_vdb:
                raise HTTPException(
                    status_code=400,
                    detail="No existing vector DB and no new changes"
                )
            return existing_vdb

        vector_db_name = f"{agent.agent_name}_vdb"

        if existing_vdb:
            existing_vdb.db_path = persist_path
            existing_vdb.name = vector_db_name
            existing_vdb.is_active = True
            vector_db = existing_vdb
        else:
            vector_db = VectorDB(
                agent_id=agent.id,
                name=vector_db_name,
                db_path=persist_path,
                is_active=True
            )
            db.add(vector_db)
        for doc in document_list:
            doc.status = DocumentStatus.embedded

        db.commit()
        db.refresh(vector_db)

        return vector_db

    except Exception as e:
        db.rollback()

        if 'document_list' in locals():
            for doc in document_list:
                doc.status = DocumentStatus.processing_failed
            db.commit()

        raise e


def get_documents_by_agent(db: Session, agent_id: int) -> List[Document]:
    return db.query(Document).filter(Document.agent_id == agent_id).all()


def get_document(db: Session, document_id: int) -> Document:
    return db.query(Document).filter(Document.id == document_id).first()


def delete_document(db: Session, document_id: int) -> bool:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True