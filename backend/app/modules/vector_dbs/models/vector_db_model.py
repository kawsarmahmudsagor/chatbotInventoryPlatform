from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base

class VectorDB(Base):
    __tablename__ = "vector_dbs"

    id       = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, unique=True)  # CHANGED + unique for 1-to-1

    name     = Column(String, nullable=False)
    db_path  = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    agent = relationship("Agent", back_populates="vector_db")                       # CHANGED