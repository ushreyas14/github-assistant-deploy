from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.auth import router as auth_router
from backend.routers.ingest import router as ingest_router
from backend.routers.query import router as query_router
from backend.routers.repos import router as repos_router
import os 

app  = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(ingest_router, prefix="/api")
app.include_router(query_router, prefix="/api/query")
app.include_router(repos_router, prefix="/api/repos")


@app.get("/health")
def health_check():
    url = os.getenv("SUPABASE_URL", "NOT_SET")
    key = os.getenv("SUPABASE_ANON_KEY", "NOT_SET")
    return {
        "status": "ok",
        "supabase_url": url,
        "supabase_key_prefix": key[:20] + "..." if key != "NOT_SET" else "NOT_SET",
        "url_has_trailing_space": url != url.strip(),
        "url_starts_with_https": url.startswith("https://"),
    }



