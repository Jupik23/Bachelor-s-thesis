from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user import UserService
from app.schemas.user_auth import UserAuthCreate, UserWithAuth, RegisterRequest
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.schemas.token import Token

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserWithAuth, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(register_request: RegisterRequest, db:Session = Depends(get_database)):
    try:
        return UserService.register_new_user(db, user_data=register_request.user_data, auth_data=register_request.user_auth_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.post("/login", response_model = Token)
def login_endpoint(login_data: UserAuthCreate, db: Session = Depends(get_database)):
    try: 
        return UserService.authenticate_user(db, login_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
