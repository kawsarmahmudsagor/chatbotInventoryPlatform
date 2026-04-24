from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from core.enums import AgentType, AgentStatus, VectorStoreType
from modules.documents.schemas.document_schema import DocumentRead
from modules.llms.schemas.llm_schema import LLMRead
from modules.vendors.schemas.vendor_schema import VendorRead

class AgentBase(BaseModel):
    vendor_id:   int
    agent_type:        AgentType
    agent_name:        str
    system_prompt:     Optional[str] = None
    llm_id:            Optional[int] = None
    llm_path:          Optional[str] = None
    vector_store_type: VectorStoreType = VectorStoreType.chroma
    status:            AgentStatus = AgentStatus.active

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    agent_name:        Optional[str]            = None
    vendor_id:   Optional[int]  = None
    system_prompt:     Optional[str]            = None
    llm_id:            Optional[int]            = None
    llm_path:          Optional[str]            = None
    vector_store_type: Optional[VectorStoreType] = None
    status:            Optional[AgentStatus]    = None

class AgentRead(AgentBase):
    id:         int
    vendor:     Optional[VendorRead] = None
    created_at: datetime
    llm:        Optional[LLMRead]    = None
    documents:  List[DocumentRead] = []

    model_config = ConfigDict(from_attributes=True)

class AgentVendorRead(BaseModel):
    id:          int
    name:        str
    is_active:   bool
    created_at:  datetime

    model_config = ConfigDict(from_attributes=True)