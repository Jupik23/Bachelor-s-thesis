from sqlalchemy.orm import Session
from app.models.oauth2 import OAuth2Account

def create_oauth2_account(db: Session, user_id: int, provider: str, provider_id: str, 
                         provider_email: str, access_token: str = None, refresh_token: str = None):
    new_auth2_accout = OAuth2Account(
        user_id=user_id,
        provider=provider,
        provider_id=provider_id,
        provider_email=provider_email,
        access_token=access_token,
        refresh_token=refresh_token
    )
    db.add(new_auth2_accout)
    db.commit()
    db.refresh(new_auth2_accout)
    db.close()

def get_oauth2_account_by_id(db: Session, provider: str, provider_id: str):
    return db.query(OAuth2Account).filter(OAuth2Account.provider== provider, OAuth2Account.provider_id == provider_id).first()

def get_oauth2_account_by_email(db: Session, provider: str, email: str):
    return db.query(OAuth2Account).filter(OAuth2Account.provider== provider, OAuth2Account.provider_email == email).first()

def get_user_by_oauth2(db: Session, provider: str, provider_id: str):
    account = get_oauth2_account_by_id(db, provider, provider_id)
    if account: 
        return account.user
    return None