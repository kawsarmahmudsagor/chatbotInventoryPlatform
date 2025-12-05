from pydantic import BaseModel, EmailStr
from typing import Optional

class VendorBase(BaseModel):
    name: str
    domain: str
    status: bool = True

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    status: Optional[bool] = None

class VendorRead(VendorBase):
    id: int

    class Config:
        orm_mode = True

