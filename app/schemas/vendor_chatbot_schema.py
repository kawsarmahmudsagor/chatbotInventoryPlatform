from pydantic import BaseModel

class VendorChatbotBase(BaseModel):
    pass

class VendorChatbotRead(VendorChatbotBase):
    id: int
    class Config:
        orm_mode = True