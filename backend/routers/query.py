from fastapi import APIRouter, Depends, HTTPException

from backend.routers.deps import AuthContext, get_auth_context
from backend.schemas.models import QueryRequest
from chain.rag_chain import build_rag_chain
from vectorstore.pinecone_store import load_vectorstore
from mongodb import load_chunks_for_repo

router = APIRouter()


@router.post("/")
async def query_repo(req: QueryRequest, auth: AuthContext = Depends(get_auth_context)):
    try:
        vectorstore = load_vectorstore(req.repo_name, auth.user_id)

        # Load full documents from MongoDB for BM25 hybrid retriever
        documents = await load_chunks_for_repo(req.repo_name, auth.user_id)

        chain, retriever = build_rag_chain(
            vectorstore, documents, top_k=req.top_k
        )

        answer = chain.invoke(req.question)
        sources = retriever.invoke(req.question)

        return {
            "repo_name": req.repo_name,
            "answer": answer,
            "sources": [
                {
                    "source": doc.metadata.get("file_path") or doc.metadata.get("source", "unknown"),
                    "chunk_preview": doc.page_content[:240],
                }
                for doc in sources
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


