from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from modules.vector_dbs.schemas.vector_db_schema import VectorDBCreate, VectorDBRead, VectorDBUpdate
from modules.vector_dbs.services import vector_db_service
from modules.vector_dbs.models.vector_db_model import VectorDB
from modules.admins.models.admin_model import Admin
from modules.auth.admins.auth_admin import get_current_admin

router = APIRouter(tags=["VectorDBs"])

@router.post("/create", response_model=VectorDBRead)
def add_vector_db(data: VectorDBCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return vector_db_service.add_vector_db(db, data)

@router.get("/", response_model=List[VectorDBRead])
def get_vector_dbs(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return vector_db_service.get_vector_dbs(db)

@router.get("/{vector_db_id}", response_model=VectorDBRead)
def get_vector_db(vector_db_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    vector_db = vector_db_service.get_vector_db(db, vector_db_id)
    if not vector_db:
        raise HTTPException(status_code=404, detail="Vector Database not found")
    return vector_db

@router.get("/agent/{agent_id}")
def get_vector_db_by_agent(agent_id: int, db: Session = Depends(get_db)):
    vdb = db.query(VectorDB).filter(VectorDB.agent_id == agent_id).first()
    return vdb  # returns null/None if not found, frontend handles it

@router.put("/update/{vector_db_id}", response_model=VectorDBRead)
def update_vector_db(vector_db_id: int, vector_db_data: VectorDBUpdate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    vector_db = vector_db_service.update_vector_db(db, vector_db_id, vector_db_data)
    if not vector_db:
        raise HTTPException(status_code=404, detail="Vector Database not found")
    return vector_db

@router.delete("/delete/{vector_db_id}")
def delete_vector_db(vector_db_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    success = vector_db_service.delete_vector_db(db, vector_db_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vector Database not found")
    return {"detail": "Vector Database deleted successfully"}
