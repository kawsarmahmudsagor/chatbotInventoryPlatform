from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from backend.db.database import Base
from chatbot.chatbotInventoryPlatform.backend.core.enums import SenderType
from datetime import datetime


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    sender_type = Column(Enum(SenderType), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=True)
    token_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="messages")
    chatbot = relationship("Chatbot", back_populates="messages")




