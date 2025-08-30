import httpx
import secrets
from urllib.parse import urlencode
from sqlalchemy.orm import Session
from app.config.oauth2 import get_provider_config
from app.crud.oauth2 import get_oauth2_account_by_id, create_oauth2_account, get_user_by_oauth2
from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.schemas.oauth2 import OAuth2UserInfo, OAuth2LoginResponse
from app.schemas.token import Token
from app.utils.jwt import generate_access_token
from typing import Dict, Any

class OAuth2Service:
    @staticmethod
    def get_authorization_url(provider: str, state: str = None):
        config = get_provider_config(provider)
        
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "scope": config["scope"],
            "response_type": "code",
            "state": state,
        }
        
        return f"{config['authorization_url']}?{urlencode(params)}"

    @staticmethod
    async def exchange_code_for_token(provider: str, code: str) -> Dict[str, Any]:
        config = get_provider_config(provider)
        
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config["redirect_uri"],
        }
        
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        
    @staticmethod
    async def get_user_info(provider: str, access_token: str):

        config = get_provider_config(provider)
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                config["user_info_url"],
                headers=headers
            )
            response.raise_for_status()
            user_data = response.json()
        
        return OAuth2Service.normalize_user_data(provider, user_data)

    @staticmethod
    def normalize_user_data(provider: str, user_data: Dict[str, Any]):
        if provider == "facebook":
            return OAuth2UserInfo(
                provider=provider,
                provider_id=str(user_data["id"]),
                email=user_data.get("email"),
                name=user_data.get("name"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                avatar_url=f"https://graph.facebook.com/{user_data['id']}/picture?type=large"
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def process_oauth2_login(db: Session, user_info: OAuth2UserInfo, access_token: str = None, refresh_token: str = None):
        
        existing_user = get_user_by_oauth2(db, user_info.provider, str(user_info.provider_id))
        is_new_user = False
        
        if existing_user:
            user = existing_user
        else:
            is_new_user = True
            user_create = UserCreate(
                name=user_info.first_name or user_info.name or "Unknown",
                surname=user_info.last_name or "",
                login=f"{user_info.provider}_{user_info.provider_id}" 
            )
            user = create_user(db, user_create)
            db.refresh(user)

            create_oauth2_account(
                db=db,
                user_id=user.id,
                provider=user_info.provider,
                provider_id=user_info.provider_id,
                provider_email=user_info.email,
                access_token=access_token,
                refresh_token=refresh_token
            )
        
        token_data = {
            "user_id": user.id,
            "email": user_info.email,
            "provider": user_info.provider
        }
        jwt_token = generate_access_token(token_data)
        
        return OAuth2LoginResponse(
            access_token=jwt_token,
            token_type="bearer",
            user={
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "login": user.login,
                "email": user_info.email
            },
            is_new_user=is_new_user
        )