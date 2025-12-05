from sqlalchemy.orm import Session
from typing import List
from chatbot.chatbotInventoryPlatform.backend.modules.users.user_model import User
from chatbot.chatbotInventoryPlatform.backend.modules.users.user_schema import UserCreate
from backend.core import auth_user

# -------------------------
# Users CRUD Operations
# -------------------------

def create_user(db: Session, user_data: UserCreate) -> User:
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        return None  # Handle in routes

    # Hash password
    hashed_password = auth_user.get_password_hash(user_data.password)

    new_user = User(
        **user_data.dict(exclude={"password"}),
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_users(db: Session) -> List[User]:
    return db.query(User).all()

def get_user(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_data: UserCreate) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    for key, value in user_data.dict().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
