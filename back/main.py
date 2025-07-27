from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.user import router
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

app.include_router(router)

#+local
if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8081, reload=True)