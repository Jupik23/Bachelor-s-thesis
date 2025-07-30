from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database.database import get_database
from app.crud.user import get_user_info_by_id
import os
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES') or 60)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def generate_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid-token",
            headers={"WWW_Authenticate": "Bearer"},
        )
    
def get_current_user_data(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        email = payload.get("email")
        user_data = {
            "user_id": user_id,
            "email": email
            }
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW_Authenticate": "Bearer"},
            )
        return user_data

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends()):
    db = next(get_database)
    try:
        user_data = get_current_user_data(token)
        user =  get_user_info_by_id(user_data["user_id"])
        if user is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW_authenticate": "Bearer"}
            )
        return user
    finally:
        db.close()