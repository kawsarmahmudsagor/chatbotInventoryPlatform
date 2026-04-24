from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime
from core.enums import AgentType, ToolStatus

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)

    agent_type = Column(SAEnum(AgentType, native_enum=False), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)    
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String, nullable=True)                    
    tool_status = Column(SAEnum(ToolStatus, native_enum=False), nullable=True, default=ToolStatus.success)
    raw_tool_input = Column(Text, nullable=True)                  
    raw_tool_output = Column(Text, nullable=True)                
    short_description = Column(Text, nullable=False)             
    user_identifier = Column(String, nullable=True)     
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    vendor = relationship("Vendor", back_populates="agent_logs")