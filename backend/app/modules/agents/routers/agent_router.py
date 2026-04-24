from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from modules.agents.schemas.agent_schema import AgentRead, AgentUpdate
from modules.agents.services import agent_service
from core.enums import AgentType, AgentStatus, VectorStoreType
from modules.admins.models.admin_model import Admin
from modules.auth.admins import auth_admin
from modules.vendors.models.vendor_model import Vendor
from modules.auth.vendors import auth_vendor

router = APIRouter(tags=["Agents"])


@router.post("/create", response_model=AgentRead)
def create_agent(
    vendor_id:   int            = Form(...),
    agent_type:        AgentType        = Form(...),
    agent_name:        str              = Form(...),
    system_prompt:     Optional[str]    = Form(None),
    llm_id:            int              = Form(...),
    llm_path:          str              = Form(...),
    vector_store_type: VectorStoreType  = Form(VectorStoreType.chroma),
    status:            AgentStatus      = Form(AgentStatus.active),
    files:             List[UploadFile] = File([]),
    db:                Session          = Depends(get_db),
    # current_admin:     Admin            = Depends(auth_admin.get_current_admin), 
):
    return agent_service.create_agent_with_documents(
        vendor_id=vendor_id,
        db=db,
        agent_type=agent_type,
        agent_name=agent_name,
        system_prompt=system_prompt,
        llm_id=llm_id,
        llm_path=llm_path,
        vector_store_type=vector_store_type,
        status=status,
        files=files or None,
    )


@router.put("/{agent_id}", response_model=AgentRead)
def update_agent(
    agent_id:          int,
    agent_name:        Optional[str]            = Form(None),
    vendor_id:   Optional[int]  = Form(None),
    system_prompt:     Optional[str]            = Form(None),
    llm_id:            Optional[int]            = Form(None),
    llm_path:          Optional[str]            = Form(None),
    vector_store_type: Optional[VectorStoreType] = Form(None),
    status:            Optional[AgentStatus]    = Form(None),
    files:             List[UploadFile]         = File([]),
    db:                Session                  = Depends(get_db),
    # current_admin:     Admin                    = Depends(auth_admin.get_current_admin),
):
    agent_data = AgentUpdate(
        agent_name=agent_name,
        vendor_id=vendor_id,
        system_prompt=system_prompt,
        llm_id=llm_id,
        llm_path=llm_path,
        vector_store_type=vector_store_type,
        status=status,
    )
    agent = agent_service.update_agent_with_documents(
        db=db, agent_id=agent_id, agent_data=agent_data, files=files or None
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("/chatbot/{chatbot_id}", response_model=List[AgentRead])
def get_agents_by_chatbot(
    chatbot_id: int,
    db: Session = Depends(get_db),
    # current_vendor: Vendor = Depends(auth_vendor.get_current_vendor),
):
    return agent_service.get_agents_by_chatbot(db, chatbot_id)


@router.get("/vendor/my-agents", response_model=List[AgentRead])
def get_my_agents(
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor),
):
    return agent_service.get_agents_by_vendor(db, current_vendor.id)


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    # current_vendor: Vendor = Depends(auth_vendor.get_current_vendor),
):
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    # current_admin: Admin = Depends(auth_admin.get_current_admin),
):
    if not agent_service.delete_agent(db, agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted"}