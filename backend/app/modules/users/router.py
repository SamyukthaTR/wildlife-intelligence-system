from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RoleChecker
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_users_me(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.organization is not None:
        current_user.organization = user_update.organization
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/admin-only")
def admin_only_endpoint(current_user: User = Depends(RoleChecker(['Administrator']))):
    return {"message": "Welcome, Admin!"}
