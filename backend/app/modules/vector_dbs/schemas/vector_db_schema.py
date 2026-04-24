from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class VectorDBBase(BaseModel):
    agent_id: int           # CHANGED
    name:     str
    db_path:  str

class VectorDBCreate(VectorDBBase):
    is_active: Optional[bool] = True

class VectorDBUpdate(BaseModel):
    agent_id:  Optional[int]  = None
    name:      Optional[str]  = None
    db_path:   Optional[str]  = None
    is_active: Optional[bool] = None

class VectorDBRead(VectorDBBase):
    id:         int
    is_active:  bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)