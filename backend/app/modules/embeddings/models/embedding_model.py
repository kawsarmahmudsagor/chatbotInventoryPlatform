from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship, validates
from db.database import Base
from core.enums import EmbeddingProvider

class Embedding(Base):
    __tablename__ = "embeddings"

    id         = Column(Integer, primary_key=True, index=True)
    vendor_id  = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)  # NEW
    model_name = Column(String, nullable=False)
    provider   = Column(Enum(EmbeddingProvider), nullable=False)
    path       = Column(String, nullable=True)

    llms   = relationship("LLM", back_populates="embedding", cascade="all, delete-orphan")
    vendor = relationship("Vendor", back_populates="embeddings")  # NEW

    @validates("provider")
    def validate_provider(self, key, value):
        value = value.lower()
        if value not in [e.value for e in EmbeddingProvider]:
            raise ValueError(f"Invalid provider '{value}'.")
        return value