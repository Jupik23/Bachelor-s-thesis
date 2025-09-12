from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user import UserService
from app.schemas.user import User
from app.schemas.user_auth import (UserAuthCreate, UserWithAuth, RegisterRequest, 
                                   PasswordUpdateRequest, PasswordUpdateResponse)
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.schemas.token import Token
from app.utils.jwt import get_current_user_data
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserWithAuth, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(register_request: RegisterRequest, db:Session = Depends(get_database)):
    try:
        return UserService.register_new_user(db, user_data=register_request.user_data, auth_data=register_request.user_auth_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.post("/tokens",response_model=Token)
def login_for_acces_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_database)):
    try:
        login_data = UserAuthCreate(
            email = form_data.username, 
            password = form_data.password
        )
        return UserService.authenticate_user(db, login_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@router.patch('/me/password', response_model=PasswordUpdateResponse)
def change_password_endpoint(change_password_data: PasswordUpdateRequest,
                             current_user: User = Depends(get_current_user_data),
                            db: Session = Depends(get_database)):
    
    if not change_password_data.password_match():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match"
        )
    
    if change_password_data.current_password == change_password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different"
        )
    try:
        UserService.change_password(
            db,
            change_password_data,
            user_id = current_user["user_id"]
        )
        return PasswordUpdateResponse(
            message="Password updated sucessfully",
            updated_at=datetime.utcnow().isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get('/me', response_model = User)
def get_current_user_endpoint(current_user: dict = Depends(get_current_user_data), db: Session = Depends(get_database)):
    try:
        user_id = current_user["user_id"]
        return UserService.get_user_info(db, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = str(e)
        )