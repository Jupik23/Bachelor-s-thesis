import os
from datetime import datetime, timedelta, date
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from app.models.oauth2 import OAuth2Account
from app.schemas.plan import PlanResponse
from app.models.meal import Meal
from app.models.medication import Medication

CLIENT_SECRETS_FILE = "client_secret.json" 
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
REDIRECT_URI = "http://localhost:8081/api/v1/integrations/google/callback"

class GoogleCalendarService:
    def __init__(self, db: Session):
        self.db = db

    def get_auth_url(self):
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
        )
        auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        return auth_url, state

    def _delete_event_if_exists(self, service, event_id):
        if not event_id:
            return
        try:
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(f"Usunięto stare wydarzenie: {event_id}")
        except Exception as e:
            print(f"Nie udało się usunąć (może już nie istnieje?): {e}")

    def get_credentials_from_code(self, code: str):
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(code=code)
        return flow.credentials

    def create_calendar_events(self, user_id: int, plan: PlanResponse, creds_data: OAuth2Account):
        
        creds = Credentials(
            token=creds_data.access_token,
            refresh_token=creds_data.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"), 
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"), 
            scopes=SCOPES
        )

        service = build('calendar', 'v3', credentials=creds)
        plan_date = plan.day_start
        db_meals = self.db.query(Meal).filter(Meal.plan_id == plan.id).all()    
        for meal in db_meals:
            if meal.google_event_id:
                self._delete_event_if_exists(service, meal.google_event_id)
            start_dt = datetime.combine(plan_date, meal.time)
            end_dt = start_dt + timedelta(minutes=30) 

            event = {
                'summary': f"Meal: {meal.description}",
                'description': f"Typ: {meal.meal_type}. Have a nice meal!",
                'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Warsaw'},
                'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Warsaw'},
                'reminders': {
                    'useDefault': False,
                    'overrides': [{'method': 'popup', 'minutes': 15}],
                },
            }
            try:
                created_event = service.events().insert(calendarId='primary', body=event).execute()
                meal.google_event_id = created_event['id']
            except Exception as e:
                print(f"Błąd dodawania posiłku: {e}")
        db_meds = self.db.query(Medication).filter(Medication.plan_id == plan.id).all()
        for med in db_meds:
            if med.google_event_id:
                self._delete_event_if_exists(service, med.google_event_id)
            start_dt = datetime.combine(plan_date, med.time)
            end_dt = start_dt + timedelta(minutes=10)

            event = {
                'summary': f"medicament: {med.name}",
                'description': f"{med.description}\Relation with meal: {med.with_meal_relation}",
                'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Warsaw'},
                'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Warsaw'},
                'reminders': {
                    'useDefault': False,
                    'overrides': [{'method': 'popup', 'minutes': 5}],
                },
                'colorId': '11' 
            }
            try:
                created_event = service.events().insert(calendarId='primary', body=event).execute()
                med.google_event_id = created_event['id']
            except Exception as e:
                print(f"Błąd dodawania leku: {e}")
        self.db.commit()
        return True