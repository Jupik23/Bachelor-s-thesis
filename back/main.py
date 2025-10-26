from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.user import router as user_router
from app.api.routes.health_form import router as healthform
from app.api.routes.auth import router as auth
from app.api.routes.intolerance import router as intolerance
from app.api.routes.preference import router as preference
from app.api.routes.meal_sugest import router as meal_sugest
from app.api.routes.medication import router as med
import uvicorn
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(healthform)
app.include_router(auth)
app.include_router(preference)
app.include_router(intolerance)
app.include_router(meal_sugest)
app.include_router(med)

#+local
if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8081, reload=True)