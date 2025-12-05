# users/interface.py

from .user_service import UserService
from .schemas import UserRead

def get_user_service() -> UserService:
    return UserService()

__all__ = ["get_user_service", "UserRead"]
