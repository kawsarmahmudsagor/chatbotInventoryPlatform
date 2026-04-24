from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db.database import get_db
from modules.agent_logs.models.agent_log_model import AgentType, ToolStatus
from modules.agent_logs.schemas.agent_log_schema import AgentLogCreate, AgentLogRead
from modules.agent_logs.services import agent_log_service
from modules.vendors.models.vendor_model import Vendor
from modules.auth.vendors import auth_vendor

router = APIRouter(tags=["Agent Logs"])


# ── Vendor-facing routes ──────────────────────────────────────────────────────

@router.get("/vendor/agent-logs", response_model=List[AgentLogRead])
def get_agent_logs(
    # Broad filter: show all logs for a specific agent type (bank / hotel)
    agent_type: Optional[AgentType] = Query(None, description="Filter by agent type: 'bank' or 'hotel'"),
    # Narrow filter: drill into a specific named agent
    agent_name: Optional[str] = Query(None, description="Filter by specific agent name e.g. 'hotel_statesman_agent'"),
    # Additional filters
    tool_name: Optional[str] = Query(None),
    tool_status: Optional[ToolStatus] = Query(None),
    user_identifier: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    """
    Returns all logs for the authenticated vendor.
    - No filters     → all logs across all agents
    - agent_type     → all logs for that type (e.g. all bank agents)
    - agent_name     → logs for one specific agent (narrowest view)
    Both filters can be combined.
    """
    return agent_log_service.get_logs_by_vendor(
        db,
        vendor_id=current_vendor.id,
        agent_type=agent_type,
        agent_name=agent_name,
        tool_name=tool_name,
        tool_status=tool_status,
        user_identifier=user_identifier,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset
    )


@router.get("/vendor/agent-logs/count")
def get_agent_log_count(
    agent_type: Optional[AgentType] = Query(None),
    agent_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    """Total log count — respects the same agent_type / agent_name filters for pagination."""
    count = agent_log_service.get_log_count_by_vendor(
        db,
        vendor_id=current_vendor.id,
        agent_type=agent_type,
        agent_name=agent_name
    )
    return {
        "vendor_id": current_vendor.id,
        "agent_type": agent_type,
        "agent_name": agent_name,
        "total_logs": count
    }


@router.get("/vendor/agent-logs/recent", response_model=List[AgentLogRead])
def get_recent_agent_logs(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    """Latest logs across ALL agents for the vendor — for a combined activity feed."""
    return agent_log_service.get_recent_logs_by_vendor(
        db, vendor_id=current_vendor.id, limit=limit
    )


@router.delete("/vendor/agent-logs/{log_id}")
def delete_agent_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    deleted = agent_log_service.delete_log(db, log_id=log_id, vendor_id=current_vendor.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"message": "Log deleted successfully"}


# ── Internal / WhatsApp bot-facing route ─────────────────────────────────────

@router.post("/internal/agent-logs", response_model=AgentLogRead)
def create_agent_log(
    log_data: AgentLogCreate,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    """Called by the WhatsApp chatbot server after every tool use."""
    return agent_log_service.create_agent_log(db, log_data)