import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db.database import get_db
from modules.agents.models.agent_model import Agent
from modules.chatbots.models.chatbot_model import Chatbot
from modules.llms.models.llm_model import LLM
from modules.embeddings.models.embedding_model import Embedding
from modules.vector_dbs.models.vector_db_model import VectorDB
from modules.documents.models.document_model import Document
from modules.vendors.models.vendor_model import Vendor
from modules.auth.vendors import auth_vendor
from utils.vectorstore_vm_helper import deploy_vectorstore_to_vm  # ← import your utility

router = APIRouter(tags=["Agent Activation"])

WA_BASE = "https://arseniuretted-shelton-unspited.ngrok-free.dev"
LOCAL_VECTORSTORE_BASE = r"C:\Users\BS23-DESKTOP-00038\Projects\chatbot\chatbotInventoryPlatform\backend\app\uploads\vectorstore\chroma"


def extract_vector_db_id(db_path: str) -> str:
    if not db_path:
        return None
    db_path = db_path.replace("\\", "/")
    if "chatbot_" not in db_path:
        raise ValueError(f"Invalid vector db path: {db_path}")
    raw_id = db_path.split("chatbot_")[-1].split("/")[0]
    return f"chatbot_{raw_id}"


class ActivateAgentRequest(BaseModel):
    agent_type: str


@router.post("/activate")
def activate_agent(
    body: ActivateAgentRequest,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor),
):
    agent_type = body.agent_type.lower()

    # ── 1. Find agent ──────────────────────────────
    agent = (
        db.query(Agent)
        .filter(
            Agent.vendor_id == current_vendor.id,
            Agent.agent_type == agent_type,
            Agent.status == "active"
        )
        .first()
    )
    if not agent:
        raise HTTPException(404, f"No active '{agent_type}' agent found")

    # ── 2. Gather config ───────────────────────────
    agent = db.query(Agent).filter(Agent.id == agent.id).first()
    llm = db.query(LLM).filter(LLM.id == agent.llm_id).first()

    embedding = None
    if llm and llm.embedding_id:
        embedding = db.query(Embedding).filter(Embedding.id == llm.embedding_id).first()

    vector_db = (
        db.query(VectorDB)
        .filter(VectorDB.agent_id == agent.id, VectorDB.is_active == True)
        .first()
    )
    if not vector_db:
        raise HTTPException(400, "No active vector DB found for this agent. Upload documents first.")

    doc = (
        db.query(Document)
        .filter(Document.agent_id == agent.id)
        .order_by(Document.created_at.desc())
        .first()
    )

    vector_db_id = extract_vector_db_id(vector_db.db_path)

    # ── 3. Deploy vectorstore files to VM ──────────
    # ── 3. Deploy vectorstore files to VM if not already there ──
    local_chroma_path = os.path.join(LOCAL_VECTORSTORE_BASE, vector_db_id)

    if not os.path.exists(local_chroma_path):
        raise HTTPException(
            400,
            f"Local vector store not found at {local_chroma_path}. Re-upload documents."
        )

    try:
        import paramiko

        VM_USER = "xr23"
        VM_HOST = "10.112.145.130"
        VM_PASSWORD = os.getenv("VM_PASSWORD")
        remote_path = f"/home/xr23/Projects/pipecat-examples/whatsapp/vectorstore/chroma/{vector_db_id}"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=VM_HOST, username=VM_USER, password=VM_PASSWORD)

        # Check if folder exists on VM
        stdin, stdout, stderr = ssh.exec_command(f"test -d {remote_path} && echo EXISTS || echo MISSING")
        result = stdout.read().decode().strip()

        if result == "EXISTS":
            # Folder already on VM — skip deploy
            ssh.close()
        else:
            # Folder missing — deploy now
            ssh.close()
            deploy_vectorstore_to_vm(local_chroma_path, vector_db.db_path)

    except Exception as e:
        raise HTTPException(502, f"Failed to check/deploy vector store to VM: {str(e)}")

    # ── 4. Build payload ───────────────────────────
    payload = {
        "agent_type": agent_type,
        "agent_name": agent_type,
        "llm_model": llm.name if llm else None,
        "embedding_model": embedding.model_name if embedding else None,
        "system_prompt": agent.system_prompt,
        "vector_db_id": vector_db_id,
        "document_address": doc.file_path if doc else None,
        "hash_address": doc.hash_address if doc else None,
    }

    # ── 5. Call WhatsApp VM ────────────────────────
    try:
        response = httpx.post(
            f"{WA_BASE}/configure-agent",
            json=payload,
            timeout=30.0  # increased — SSH + file copy can take a moment
        )
        if response.status_code != 200:
            raise HTTPException(502, f"WhatsApp server error: {response.text}")
    except httpx.RequestError as e:
        raise HTTPException(503, f"VM unreachable: {str(e)}")

    return {
        "status": "success",
        "agent_type": agent_type,
        "vector_db_id": vector_db_id,
    }