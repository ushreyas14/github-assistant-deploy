from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.auth import router as auth_router
from backend.routers.ingest import router as ingest_router
from backend.routers.query import router as query_router
from backend.routers.repos import router as repos_router

app  = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(ingest_router, prefix="/api")
app.include_router(query_router, prefix="/api/query")
app.include_router(repos_router, prefix="/api/repos")


@app.get('/health')
def gethealth():
    return {"status": "okay"}



