from fastapi import FastAPI
from backend.routers.ingest import router

app  = FastAPI()

app.include_router(router, prefix='/api')

@app.get('/health')
def gethealth():
    return {"status": "okay"}


