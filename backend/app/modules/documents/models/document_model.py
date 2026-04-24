from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base
from core.enums import DocumentStatus

class Document(Base):
    __tablename__ = "documents"

    id           = Column(Integer, primary_key=True, index=True)
    agent_id     = Column(Integer, ForeignKey("agents.id"), nullable=False)
    title        = Column(String, nullable=False)
    file_path    = Column(String, nullable=False)
    hash_address = Column(String, nullable=True)   # NEW
    status       = Column(Enum(DocumentStatus), default=DocumentStatus.processing)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)

    agent = relationship("Agent", back_populates="documents")