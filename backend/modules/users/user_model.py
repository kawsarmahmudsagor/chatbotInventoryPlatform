from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from backend.db.database import Base
from chatbot.chatbotInventoryPlatform.backend.core.enums import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.external)
    is_active = Column(Boolean, default=True)

    vendor = relationship("Vendor", back_populates="users")
    messages = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

