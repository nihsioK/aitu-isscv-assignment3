from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.user import User, Role


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def require_client(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.CLIENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Client access required")
    return current_user
