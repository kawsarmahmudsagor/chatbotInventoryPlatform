import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    vendor = "vendor"
    external = "external"

class UserType(str, enum.Enum):
    vendor = "vendor"
    external = "external"
    admin = "admin"

class SenderType(str, enum.Enum):
    vendor = "vendor"
    external = "external"
    chatbot = "chatbot"
    admin = "admin"

class VendorStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class ChatbotStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"    

class DocumentStatus(str, enum.Enum):
    processing = "processing"
    embedded = "embedded"
    processing_failed = "processing_failed"

class APIKeyStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class LLMProvider(str, enum.Enum):
    openai = "openai"
    anthropic = "anthropic"
    cohere = "cohere"
    huggingface = "huggingface"
    google = "google"
    azure = "azure"
    local = "local"
    ollama="ollama"

class EmbeddingProvider(str, enum.Enum):
    openai = "openai"
    cohere = "cohere"
    huggingface = "huggingface"
    ollama = "ollama"
    local = "local"

class VectorStoreType(str, enum.Enum):
    chroma = "chroma"
    faiss = "faiss"


class AgentType(str, enum.Enum):
    bank = "bank"
    hotel = "hotel"

class AgentStatus(str, enum.Enum):
    active   = "active"
    inactive = "inactive"

class ToolStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    error = "error"