from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.database import Base
from chatbot.chatbotInventoryPlatform.backend.core.enums import ChatbotMode

class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    llm_id = Column(Integer, ForeignKey("llms.id"))
    vector_db = Column(String, nullable=False)
    mode = Column(Enum(ChatbotMode), default=ChatbotMode.private)
    is_active = Column(Boolean, default=True)
    token_limit = Column(Integer, nullable=False)
    context_limit = Column(Integer, nullable=False)
    
    vendor = relationship("Vendor", back_populates="chatbots")
    llm = relationship("LLM", back_populates="chatbots")
    documents = relationship("Document", back_populates="chatbot", cascade="all, delete-orphan")
    messages = relationship("Conversation", back_populates="chatbot", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="chatbot")




