from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import List, Optional

from modules.agents.models.agent_model import Agent
from modules.agents.schemas.agent_schema import AgentCreate, AgentUpdate
from modules.documents.services.document_service import create_documents_bulk, embed_document
from core.enums import DocumentStatus, AgentStatus, VectorStoreType


def create_agent_with_documents(
    db: Session,
    vendor_id:int,
    agent_type: str,
    agent_name: str,
    system_prompt: Optional[str] = None,
    llm_id: Optional[int] = None,
    llm_path: Optional[str] = None,
    vector_store_type: VectorStoreType = VectorStoreType.chroma,
    status: AgentStatus = AgentStatus.active,
    files: List[UploadFile] = None,
) -> Agent:

    agent = Agent(
        vendor_id=vendor_id,
        agent_type=agent_type,
        agent_name=agent_name,
        system_prompt=system_prompt,
        llm_id=llm_id,
        llm_path=llm_path,
        vector_store_type=vector_store_type,
        status=status,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    if files:
        saved_docs = create_documents_bulk(db, agent.id, files)

        if saved_docs:
            try:
                # IMPORTANT: embed ALL docs, not just first
                for doc in saved_docs:
                    embed_document(db, doc.id)

            except Exception as e:
                for doc in saved_docs:
                    doc.status = DocumentStatus.processing_failed
                db.commit()
                raise e

    return agent


def update_agent_with_documents(
    db: Session,
    vendor_id:int,
    agent_id: int,
    agent_data: AgentUpdate,
    files: List[UploadFile] = None,
) -> Optional[Agent]:

    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return None
    
    if agent.vendor_id!=vendor_id:
        return None
        
    if agent_data.vendor_id is not None:
        agent.vendor_id = agent_data.vendor_id

    if agent_data.agent_name is not None:
        agent.agent_name = agent_data.agent_name

    if agent_data.system_prompt is not None:
        agent.system_prompt = agent_data.system_prompt

    if agent_data.llm_id is not None:
        agent.llm_id = agent_data.llm_id

    if agent_data.llm_path is not None:
        agent.llm_path = agent_data.llm_path

    if agent_data.vector_store_type is not None:
        agent.vector_store_type = agent_data.vector_store_type

    if agent_data.status is not None:
        agent.status = agent_data.status

    db.commit()
    db.refresh(agent)

    if files:
        saved_docs = create_documents_bulk(db, agent.id, files)
        if saved_docs:
            try:
                for doc in saved_docs:
                    embed_document(db, doc.id)
            except Exception as e:
                for doc in saved_docs:
                    doc.status = DocumentStatus.processing_failed
                db.commit()
                raise e
    return agent


def get_agent(db: Session, agent_id: int) -> Optional[Agent]:
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agents_by_chatbot(db: Session, chatbot_id: int) -> List[Agent]:
    return db.query(Agent).filter(Agent.chatbot_id == chatbot_id).all()


def get_agents_by_vendor(db: Session, vendor_id: int) -> List[Agent]:
    return (
        db.query(Agent)
        .filter(Agent.vendor_id == vendor_id)
        .all()
    )


def delete_agent(db: Session, agent_id: int) -> bool:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return False
    db.delete(agent)
    db.commit()
    return True