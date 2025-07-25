from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/hello")
def hello():
    return {"message": "CORS is working!"}

@app.post("/siema")
def siema():
    return {"message": "CORS is working!"}


#local
# if __name__=="__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8081, reload=True)