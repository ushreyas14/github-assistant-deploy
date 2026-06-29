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
    supa_key = os.getenv("SUPABASE_ANON_KEY", "NOT_SET")
    pine_key = os.getenv("PINECONE_API_KEY", "NOT_SET")
    groq_key = os.getenv("GROQ_API_KEY", "NOT_SET")
    pine_idx = os.getenv("PINECONE_INDEX_NAME", "NOT_SET")
    return {
        "status": "ok",
        "supabase_url": url.strip() if url else url,
        "supabase_key_set": supa_key != "NOT_SET",
        "pinecone_key_prefix": (pine_key[:10] + "...") if pine_key != "NOT_SET" else "NOT_SET",
        "pinecone_key_has_newline": "\n" in pine_key,
        "pinecone_key_has_trailing_space": pine_key != pine_key.strip(),
        "pinecone_index": pine_idx.strip() if pine_idx else pine_idx,
        "groq_key_set": groq_key != "NOT_SET",
    }



