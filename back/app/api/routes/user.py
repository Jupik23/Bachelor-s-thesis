from fastapi import APIRouter, Depends, HTTPException, status, Body
from app.services.user import UserService
from app.services.oauth2 import OAuth2Service
from app.schemas.user import User
from app.schemas.user_auth import (UserAuthCreate, UserWithAuth, RegisterRequest, 
                                   PasswordUpdateRequest, PasswordUpdateResponse)
from app.schemas.oauth2 import OAuth2CallbackRequest, OAuth2LoginResponse
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.schemas.token import Token
from app.utils.jwt import get_current_user_data
from fastapi.security import OAuth2PasswordRequestForm
import secrets
import os 
from dotenv import load_dotenv

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
    
@router.post("/token",response_model=Token)
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
    
@router.put('/password', response_model=PasswordUpdateResponse)
def change_password_endpoint(change_password_data: PasswordUpdateRequest,
                             current_user: User = Depends(get_current_user_data),
                            db: Session = Depends(get_database)):
    
    if not change_password_data.password_match():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match"
        )
    
    if change_password_data.current_password == change_password_data.new_passoword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different"
        )
    try:
        UserService.change_password(
            db,
            change_password_data,
            user_id = current_user["id"]
        )
        return {"detail": "Password updated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get('/me', response_model = User)
def get_current_user_endpoint(current_user: dict = Depends(get_current_user_data), db: Session = Depends(get_database)):
    try:
        user_id = current_user["user_id"]
        return UserService.get_info_by_id(db, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = str(e)
        )

@router.get("/auth/{provider}")
def oauth2_login(provider: str):
    try:
        state = secrets.token_urlsafe(32)
        authorization_url = OAuth2Service.get_authorization_url(provider, state)
        return {"authorization_url": authorization_url, "state": state}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/auth/{provider}/callback")
async def oauth2_callback(provider: str, code: str, state: str = None, db: Session = Depends(get_database)
):
    try:
        token_data = await OAuth2Service.exchange_code_for_token(provider, code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token"
            )
        
        user_info = await OAuth2Service.get_user_info(provider, access_token)
        login_response = OAuth2Service.process_oauth2_login(
            db, user_info, access_token, refresh_token
        )
        return login_response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth2 authentication failed: {str(e)}"
        )

@router.post("/auth/{provider}/mobile")
async def oauth2_mobile_login(provider: str,callback_request: OAuth2CallbackRequest = Body(...),db: Session = Depends(get_database)):
    try:
        token_data = await OAuth2Service.exchange_code_for_token(provider, callback_request.code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token"
            )
        user_info = await OAuth2Service.get_user_info(provider, access_token)
        
        return OAuth2Service.process_oauth2_login(
            db, user_info, access_token, refresh_token
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth2 authentication failed: {str(e)}"
        )
