from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.database import Base

class LLM(Base):
    __tablename__ = "llms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    embedding_id = Column(Integer, ForeignKey("embeddings.id"), nullable=False)
    def_token_limit = Column(Integer, nullable=False)
    def_context_limit = Column(Integer, nullable=False)

    chatbots = relationship("Chatbot", back_populates="llm")
    embedding = relationship("Embedding", back_populates="llms")


