from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.models import IngestRequest
from backend.routers.deps import AuthContext, get_auth_context
from backend.db.supabase_client import save_repo
from ingestion.cloner import clone_or_pull
from ingestion.loader import load_repo_documents
from ingestion.chunker import chunk_documents
from vectorstore.pinecone_store import ingest_to_pinecone
from mongodb import store_chunks_metadata

router = APIRouter()

@router.post('/ingest')
async def ingest(req: IngestRequest, auth: AuthContext = Depends(get_auth_context)):
    try:
        path, name = clone_or_pull(req.repo_url)
        docs = load_repo_documents(path)
        chunks = chunk_documents(docs)

        # MongoDB provides full metadata for hybrid retrieval, but Pinecone also
        # stores the chunk text. Continue ingestion if MongoDB is unavailable so
        # the repository remains queryable with vector retrieval alone.
        metadata_store = "mongodb"
        try:
            await store_chunks_metadata(chunks, name, auth.user_id)
        except Exception as exc:
            metadata_store = "pinecone_only"
            print(f"MongoDB chunk storage failed; continuing with Pinecone: {exc}")

        # Store trimmed metadata + embeddings in Pinecone
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
            "chunks": len(chunks),
            "metadata_store": metadata_store,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

