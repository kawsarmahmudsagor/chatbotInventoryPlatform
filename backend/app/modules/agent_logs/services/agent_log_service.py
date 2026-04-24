from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from modules.agent_logs.models.agent_log_model import AgentLog, AgentType, ToolStatus
from modules.agent_logs.schemas.agent_log_schema import AgentLogCreate


def create_agent_log(db: Session, log_data: AgentLogCreate) -> AgentLog:
    log = AgentLog(**log_data.dict())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_logs_by_vendor(
    db: Session,
    vendor_id: int,
    agent_type: Optional[AgentType] = None,   # e.g. "bank" | "hotel" — broad filter
    agent_name: Optional[str] = None,          # e.g. "hotel_statesman_agent" — narrow filter
    tool_name: Optional[str] = None,
    tool_status: Optional[ToolStatus] = None,
    user_identifier: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0
) -> List[AgentLog]:
    query = db.query(AgentLog).filter(AgentLog.vendor_id == vendor_id)

    if agent_type:
        query = query.filter(AgentLog.agent_type == agent_type)
    if agent_name:
        query = query.filter(AgentLog.agent_name == agent_name)
    if tool_name:
        query = query.filter(AgentLog.tool_name == tool_name)
    if tool_status:
        query = query.filter(AgentLog.tool_status == tool_status)
    if user_identifier:
        query = query.filter(AgentLog.user_identifier == user_identifier)
    if from_date:
        query = query.filter(AgentLog.created_at >= from_date)
    if to_date:
        query = query.filter(AgentLog.created_at <= to_date)

    return (
        query
        .order_by(desc(AgentLog.created_at))
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_log_count_by_vendor(
    db: Session,
    vendor_id: int,
    agent_type: Optional[AgentType] = None,
    agent_name: Optional[str] = None,
) -> int:
    query = db.query(AgentLog).filter(AgentLog.vendor_id == vendor_id)

    if agent_type:
        query = query.filter(AgentLog.agent_type == agent_type)
    if agent_name:
        query = query.filter(AgentLog.agent_name == agent_name)

    return query.count()


def get_recent_logs_by_vendor(
    db: Session,
    vendor_id: int,
    limit: int = 20
) -> List[AgentLog]:
    return (
        db.query(AgentLog)
        .filter(AgentLog.vendor_id == vendor_id)
        .order_by(desc(AgentLog.created_at))
        .limit(limit)
        .all()
    )


def delete_log(db: Session, log_id: int, vendor_id: int) -> bool:
    log = db.query(AgentLog).filter(
        AgentLog.id == log_id,
        AgentLog.vendor_id == vendor_id
    ).first()
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True