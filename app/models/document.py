from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config.database import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    chunk_summary = Column(String, nullable = False)
    summary = Column(Text, nullable=False)
    tags = Column(String, nullable=False)
    chatbot_id = Column(Integer, ForeignKey("chatbot.id"), nullable=False)
    uploaded_by_id_vendor = Column(Integer, ForeignKey("vendor.id"), nullable=True)
    uploaded_by_id_admin = Column(Integer, ForeignKey("admin.id"), nullable=True)

    uploaded_by_vendor = relationship("Vendor", back_populates="documents")
    uploaded_by_admin = relationship("Admin", back_populates="documents")
    chatbot = relationship("Chatbot", back_populates="documents")