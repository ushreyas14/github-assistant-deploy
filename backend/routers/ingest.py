from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.models import IngestRequest
from backend.routers.deps import AuthContext, get_auth_context
from backend.db.supabase_client import save_repo
from ingestion.cloner import clone_or_pull
from ingestion.loader import load_repo_documents
from ingestion.chunker import chunk_documents
from vectorstore.pinecone_store import ingest_to_pinecone

router = APIRouter()

@router.post('/ingest')
def ingest(req: IngestRequest, auth: AuthContext = Depends(get_auth_context)):
    try:
        path, name = clone_or_pull(req.repo_url)
        docs = load_repo_documents(path)
        chunks = chunk_documents(docs)

        ingest_to_pinecone(chunks, name, auth.user_id)
        namespace = save_repo(
            user_id=auth.user_id,
            repo_name=name,
            repo_url=req.repo_url,
            chunk_count=len(chunks),
            access_token=auth.access_token,
        )

        return {
            "status": "success",
            "repo_name": name,
            "namespace": namespace,
            "chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
