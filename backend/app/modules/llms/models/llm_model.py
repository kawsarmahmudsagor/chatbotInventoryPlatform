from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, validates
from db.database import Base
from core.enums import LLMProvider

class LLM(Base):
    __tablename__ = "llms"

    id                = Column(Integer, primary_key=True, index=True)
    vendor_id         = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)  # NEW
    name              = Column(String, nullable=False)
    provider          = Column(Enum(LLMProvider), nullable=False)
    embedding_id      = Column(Integer, ForeignKey("embeddings.id"), nullable=False)
    def_token_limit   = Column(Integer, nullable=False)
    def_context_limit = Column(Integer, nullable=False)
    path              = Column(String, nullable=True)

    chatbots  = relationship("Chatbot", back_populates="llm", cascade="all, delete-orphan")
    agents    = relationship("Agent", back_populates="llm", cascade="all, delete-orphan")
    embedding = relationship("Embedding", back_populates="llms")
    vendor    = relationship("Vendor", back_populates="llms")  # NEW

    @validates("provider")
    def validate_provider(self, key, value):
        value = value.lower()
        if value not in [e.value for e in LLMProvider]:
            raise ValueError(f"Invalid provider '{value}'.")
        return value