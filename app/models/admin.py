from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False, default="admin")
    hashed_password = Column(String, nullable=False)

    conversations = relationship("ConversationHistory", back_populates="user")
    documents = relationship("Document", back_populates="uploaded_by_admin")