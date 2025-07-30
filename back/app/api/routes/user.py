from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user import UserService
from app.schemas.user import User
from app.schemas.user_auth import UserAuthCreate, UserWithAuth, RegisterRequest
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.schemas.token import Token
from app.utils.jwt import get_current_user_data
from fastapi.security import OAuth2PasswordRequestForm

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
    
@router.post('/change_password')
def change_password_endpoint():
    pass
    

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
