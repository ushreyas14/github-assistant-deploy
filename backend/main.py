from fastapi import FastAPI
from backend.routers.auth import router as auth_router

app  = FastAPI()

app.include_router(auth_router, prefix="/api/auth")


@app.get('/health')
def gethealth():
    return {"status": "okay"}



