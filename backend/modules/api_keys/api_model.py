from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from backend.db.database import Base
from chatbot.chatbotInventoryPlatform.backend.core.enums import APIKeyStatus

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=True)
    key = Column(String, unique=True, nullable=False)
    status = Column(Enum(APIKeyStatus), default=APIKeyStatus.active)

    vendor = relationship("Vendor", back_populates="api_keys")
    chatbot = relationship("Chatbot", back_populates="api_keys")
