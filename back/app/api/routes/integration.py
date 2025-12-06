from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import RedirectResponse
from datetime import date
from sqlalchemy import delete
from sqlalchemy.orm import Session
from app.database.database import get_database
from app.services.google_calendar import GoogleCalendarService
from app.services.plan import PlanCreationService
from app.crud.oauth2 import create_oauth2_account, get_oauth2_account_by_id
from app.utils.jwt import get_current_user 
from app.models.oauth2 import OAuth2Account

router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations"])

@router.get("/google/auth-url")
def google_auth(db: Session = Depends(get_database)):
    service = GoogleCalendarService(db)
    url, state = service.get_auth_url()
    return {"authorization_url": url, "state": state}

@router.get("/google/callback")
def google_callback(code: str, state: str, request: Request, db: Session = Depends(get_database)):
    FRONTEND_URL = "http://localhost"
    return RedirectResponse(f"{FRONTEND_URL}/todays-plan?google_code={code}")

@router.post("/google/connect")
def connect_google(data: dict, current_user = Depends(get_current_user), db: Session = Depends(get_database)):
    code = data.get("code")
    service = GoogleCalendarService(db)
    creds = service.get_credentials_from_code(code)
    create_oauth2_account(
        db=db,
        user_id=current_user.id,
        provider="google_calendar",
        provider_id="calendar", 
        provider_email="user@gmail.com", 
        access_token=creds.token,
        refresh_token=creds.refresh_token
    )
    return {"message": "Google Calendar connected"}

@router.post("/google/sync")
async def sync_calendar(
    payload: dict = Body(...),
    current_user = Depends(get_current_user), db: Session = Depends(get_database)):
    date_str = payload.get("plan_date")
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    creds_db = get_oauth2_account_by_id(db, provider="google_calendar", provider_id="calendar")
    if not creds_db:
        raise HTTPException(status_code=400, detail="Google Calendar not connected")
    plan_service = PlanCreationService(db)
    plan = await plan_service.get_plan_by_date(user_id=current_user.id, plan_date=target_date)
    
    if not plan or (not plan.meals and not plan.medications):
         raise HTTPException(status_code=404, detail=f"No plan found for {target_date}")
    gc_service = GoogleCalendarService(db)
    gc_service.create_calendar_events(current_user.id, plan, creds_db)
    
    return {"message": f"Plan for {target_date} synced to Google Calendar!"}

@router.get("/google/status")
def get_google_status(current_user = Depends(get_current_user), db: Session = Depends(get_database)):
    creds = get_oauth2_account_by_id(db, provider="google_calendar", provider_id="calendar")    
    account = db.query(OAuth2Account).filter(
        OAuth2Account.user_id == current_user.id,
        OAuth2Account.provider == "google_calendar"
    ).first()
    return {"is_connected": account is not None}
@router.delete("/google/disconnect")
def disconnect_google(current_user: dict = Depends(get_current_user), db: Session=Depends(get_database)):
    stmt = delete(OAuth2Account).where(
        OAuth2Account.user_id == current_user.id,
        OAuth2Account.provider =="google_calendar"
    )
    result = db.execute(stmt)
    db.commit()
    if result.rowcount==0:
        raise  HTTPException(status_code=404, detail="Integration not found")
    return {"message": "Disconnected from Google Calendar"}