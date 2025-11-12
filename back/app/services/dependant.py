from sqlalchemy.orm import Session
from typing import List
from app.schemas.dependent import DependentCreateRequest
from app.schemas.user_auth import UserAuthCreate
from app.models.user import User
from app.crud import user as crud_user
from app.crud import user_auth as crud_user_auth
from app.crud import care_relation as crud_care_relation
from app.services.user import UserService

class DependentService:
    def __init__(self, db: Session):
        self.db = db

    def create_dependent_account(self, carer_id: int, request: DependentCreateRequest) -> User:
        
        if crud_user_auth.get_user_auth_by_email(self.db, email_adress=request.user_auth_data.email):
            raise ValueError("Użytkownik z tym adresem email już istnieje.")
        
        if crud_user.get_user_info_by_login(self.db, account_login=request.user_data.login):
            raise ValueError("Użytkownik z tym loginem już istnieje.")

        try:
            new_user = crud_user.create_user(self.db, acount_data=request.user_data)
            
            hashed_password = UserService.hash_password(request.user_auth_data.password)
           
            auth_data_hashed = UserAuthCreate(
                email=request.user_auth_data.email, 
                password=hashed_password
            )
            crud_user_auth.create_new_user_auth(
                self.db, 
                auth_data=auth_data_hashed, 
                user_id=new_user.id
            )
            crud_care_relation.create_care_relation(
                self.db, 
                carer_id=carer_id, 
                patient_id=new_user.id
            )
            self.db.commit()
            self.db.refresh(new_user)
            return new_user

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Nie udało się utworzyć konta: {e}")

    def get_my_dependents(self, carer_id: int) -> List[User]:
        dependents = crud_care_relation.get_dependents_by_carer_id(self.db, carer_id=carer_id)
        return dependents