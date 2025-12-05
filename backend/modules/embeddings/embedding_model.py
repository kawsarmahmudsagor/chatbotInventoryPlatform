from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.database import Base

class Embedding(Base):
    __tablename__ = "embeddings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model_name = Column(String, nullable=False)

    llms = relationship("LLM", back_populates="embedding")