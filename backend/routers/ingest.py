from fastapi import APIRouter
from backend.schemas.models import IngestRequest
from ingestion.cloner import clone_or_pull
from ingestion.loader import load_repo_documents
from ingestion.chunker import chunk_documents
from vectorstore.pinecone_store import ingest_to_pinecone

router = APIRouter()

@router.post('/ingest')
def ingest(req: IngestRequest):
    path, name = clone_or_pull(req.repo_url)
    docs = load_repo_documents(path)
    chunks = chunk_documents(docs)

    ingest_to_pinecone(chunks, name, req.user_id)

    return {
        "status": "success",
        "repo_name": name,
        "chunks": len(chunks)
    }