from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user import UserService
from app.schemas.user import UserCreate
from app.schemas.user_auth import UserAuthCreate, UserWithAuth
from sqlalchemy.orm import Session
from app.database.database import get_database
router = APIRouter(prefix="/users")

@router.post("/register", response_model=UserWithAuth, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user_data: UserCreate, user_auth_data: UserAuthCreate, db:Session = Depends(get_database)):
    try:
        return UserService.register_new_user(db, user_data, user_auth_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    

