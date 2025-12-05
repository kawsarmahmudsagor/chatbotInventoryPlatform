from pydantic import BaseModel, EmailStr
from typing import Optional
from chatbot.chatbotInventoryPlatform.backend.core.enums import UserRole

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.external
    is_active: bool = True
    vendor_id: Optional[int] = None

class UserCreate(UserBase):
    password: str  

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    vendor_id: Optional[int] = None

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True

