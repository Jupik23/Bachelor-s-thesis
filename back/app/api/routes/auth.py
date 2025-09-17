from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.schemas.user_auth import UserAuthCreate
from app.services.user import UserService
from app.services.oauth2 import OAuth2Service
from app.schemas.oauth2 import OAuth2CallbackRequest
from app.schemas.token import Token
import secrets

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/session", response_model = Token)
def login_endpoint(login_data: UserAuthCreate, db: Session = Depends(get_database)):
    try: 
        return UserService.authenticate_user(db, login_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
@router.get("/{provider}")
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

@router.get("/{provider}/callback")
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

# @router.post("/{provider}/mobile")
# async def oauth2_mobile_login(provider: str,callback_request: OAuth2CallbackRequest = Body(...),db: Session = Depends(get_database)):
#     try:
#         token_data = await OAuth2Service.exchange_code_for_token(provider, callback_request.code)
#         access_token = token_data.get("access_token")
#         refresh_token = token_data.get("refresh_token")
        
#         if not access_token:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Failed to get access token"
#             )
#         user_info = await OAuth2Service.get_user_info(provider, access_token)
        
#         return OAuth2Service.process_oauth2_login(
#             db, user_info, access_token, refresh_token
#         )
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"OAuth2 authentication failed: {str(e)}"
#         )