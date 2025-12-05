from sqlalchemy.orm import Session
from typing import List
from backend.models.api_keys import APIKey
from backend.schemas.api_keys import APIKeyCreate

# -------------------------
# CRUD Operations
# -------------------------

def create_api_key(db: Session, api_key_data: APIKeyCreate) -> APIKey:
    new_key = APIKey(**api_key_data.dict())
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return new_key


def get_api_keys(db: Session) -> List[APIKey]:
    return db.query(APIKey).all()


def get_api_key(db: Session, key_id: int) -> APIKey:
    return db.query(APIKey).get(key_id)


def update_api_key(db: Session, key_id: int, api_key_data: APIKeyCreate) -> APIKey:
    key = db.query(APIKey).get(key_id)
    if not key:
        return None
    for k, v in api_key_data.dict().items():
        setattr(key, k, v)
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


def delete_api_key(db: Session, key_id: int) -> bool:
    key = db.query(APIKey).get(key_id)
    if not key:
        return False
    db.delete(key)
    db.commit()
    return True
