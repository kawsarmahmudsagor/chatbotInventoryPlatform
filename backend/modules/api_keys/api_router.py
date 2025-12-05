from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.database import get_db
from backend.schemas.api_keys import APIKeyCreate, APIKeyRead
from backend.api_keys import operations

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

# Create API Key
@router.post("/", response_model=APIKeyRead)
def create_api_key(api_key: APIKeyCreate, db: Session = Depends(get_db)):
    return operations.create_api_key(db, api_key)

# Get all API Keys
@router.get("/", response_model=List[APIKeyRead])
def get_api_keys(db: Session = Depends(get_db)):
    return operations.get_api_keys(db)

# Get single API Key
@router.get("/{key_id}", response_model=APIKeyRead)
def get_api_key(key_id: int, db: Session = Depends(get_db)):
    key = operations.get_api_key(db, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
    return key

# Update API Key
@router.put("/{key_id}", response_model=APIKeyRead)
def update_api_key(key_id: int, api_key_data: APIKeyCreate, db: Session = Depends(get_db)):
    key = operations.update_api_key(db, key_id, api_key_data)
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
    return key

# Delete API Key
@router.delete("/{key_id}")
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    success = operations.delete_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API Key not found")
    return {"detail": "API Key deleted successfully"}
