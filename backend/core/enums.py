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

class DocumentStatus(str, enum.Enum):
    processing = "processing"
    ready = "ready"
    failed = "failed"

class ChatbotMode(str, enum.Enum):
    private = "private"
    public = "public"

class APIKeyStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
