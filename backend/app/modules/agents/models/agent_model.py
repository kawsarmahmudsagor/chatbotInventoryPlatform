from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base
from core.enums import AgentType, AgentStatus, VectorStoreType

class Agent(Base):
    __tablename__ = "agents"

    id               = Column(Integer, primary_key=True, index=True)
    vendor_id   = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    agent_type       = Column(SAEnum(AgentType, native_enum=False), nullable=False, index=True)
    agent_name       = Column(String, nullable=False)
    system_prompt    = Column(Text, nullable=True)
    llm_id      = Column(Integer, ForeignKey("llms.id"))
    llm_path    = Column(String, nullable=False)
    vector_store_type = Column(SAEnum(VectorStoreType, native_enum=False),
                               default=VectorStoreType.chroma, nullable=False)
    status           = Column(SAEnum(AgentStatus, native_enum=False),
                               default=AgentStatus.active, nullable=False)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    vendor     = relationship("Vendor", back_populates="agents")
    llm        = relationship("LLM", back_populates="agents")
    documents  = relationship("Document", back_populates="agent",
                              cascade="all, delete-orphan")
    vector_db  = relationship("VectorDB", back_populates="agent",
                              uselist=False, cascade="all, delete-orphan")