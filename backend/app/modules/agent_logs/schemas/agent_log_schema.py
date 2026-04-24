from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from modules.agent_logs.models.agent_log_model import AgentType, ToolStatus


class AgentLogCreate(BaseModel):
    agent_type: AgentType
    agent_name: str
    vendor_id: int
    tool_name: Optional[str] = None
    tool_status: Optional[ToolStatus] = ToolStatus.success
    raw_tool_input: Optional[str] = None
    raw_tool_output: Optional[str] = None
    short_description: str
    user_identifier: Optional[str] = None


class AgentLogRead(BaseModel):
    id: int
    agent_type: AgentType
    agent_name: str
    vendor_id: int
    tool_name: Optional[str]
    tool_status: Optional[ToolStatus]
    raw_tool_input: Optional[str]
    raw_tool_output: Optional[str]
    short_description: str
    user_identifier: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentLogFilter(BaseModel):
    """Optional filters for querying logs"""
    tool_name: Optional[str] = None
    tool_status: Optional[ToolStatus] = None
    user_identifier: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None