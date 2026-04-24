from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class Chatbot(Base):
    __tablename__ = "chatbots"

    id          = Column(Integer, primary_key=True, index=True)
    vendor_id   = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    name        = Column(String, nullable=False)
    description = Column(Text)
    llm_id      = Column(Integer, ForeignKey("llms.id"))
    llm_path    = Column(String, nullable=False)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    vendor        = relationship("Vendor", back_populates="chatbots")
    llm           = relationship("LLM", back_populates="chatbots")
    conversations = relationship("Conversation", back_populates="chatbot",
                                 cascade="all, delete-orphan")
    api_keys      = relationship("APIKey", back_populates="chatbot",
                                 cascade="all, delete-orphan")