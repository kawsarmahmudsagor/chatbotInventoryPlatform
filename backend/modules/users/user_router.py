from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.database import get_db
from chatbot.chatbotInventoryPlatform.backend.modules.users.user_schema import UserCreate, UserRead
from chatbot.chatbotInventoryPlatform.backend.modules.users import operations as user_ops
from chatbot.chatbotInventoryPlatform.backend.modules.users.user_model import User
from backend.core import auth_user, auth_vendor
from chatbot.chatbotInventoryPlatform.backend.modules.vendors.vendor_model import Vendor

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/create", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = user_ops.create_user(db, user)
    if not new_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return new_user

@router.get("/", response_model=List[UserRead])
def get_users(
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    return user_ops.get_users(db)

@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_user.get_current_user)
):
    user = user_ops.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_user.get_current_user)
):
    updated_user = user_ops.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_user.get_current_user)
):
    success = user_ops.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
