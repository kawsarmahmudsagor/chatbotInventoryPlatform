from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from backend.db.database import Base

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    status = Column(Boolean, default=True)

    users = relationship("User", back_populates="vendor")
    chatbots = relationship("Chatbot", back_populates="vendor")
    documents = relationship("Document", back_populates="vendor")
    api_keys = relationship("APIKey", back_populates="vendor")
