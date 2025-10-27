from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.services.spoonacular import Spoonacular
from app.schemas.spoonacular import ComplexSearchResponse
from app.schemas.health_form import HealthFormCreate 
from app.services.health_form import HealthFormService 
from app.utils.jwt import get_current_user 
from app.models.user import User 
from typing import List, Optional
router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])

@router.get("/search", response_model=ComplexSearchResponse)
async def search_recipes_endpoint(
    q: str,
    limit: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
): 

    health_form_service = HealthFormService(db)
    user_health_form_model = health_form_service.get_health_form(user_id=current_user.id)
    
    if not user_health_form_model:
        raise HTTPException(
            status_code=400, 
            detail="Health Form not found. Please fill out your health form first."
        )
        
    try:
        user_health_form_data = HealthFormCreate.model_validate(user_health_form_model.__dict__)
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error validating HealthForm data: {e}")

    service = Spoonacular()
    try:
        results = await service.search_recipes(
            query=q, 
            health_form=user_health_form_data, 
            number=limit
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Błąd podczas wyszukiwania przepisów: {e}"
        )