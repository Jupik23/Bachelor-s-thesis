from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.utils.jwt import get_current_user
from app.services.plan import PlanCreationService
from app.schemas.plan import PlanResponse

router = APIRouter(prefix="/api/v1/meals",  tags=["meals"])

@router.post("/generate", response_model=PlanResponse)
async def generate_plan(db: Session = Depends(get_database), 
                        user: Session = Depends(get_current_user),
                        range: str = "day"):
    if range != "day":
         raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="In progress..."
        )

    plan_service = PlanCreationService(db)
    
    try:
        new_plan = await plan_service.generate_and_save_plan(
            user_id=user.id, 
            created_by_id=user.id, 
            time_frame=range
        )
        return new_plan
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error: {e}"
        )