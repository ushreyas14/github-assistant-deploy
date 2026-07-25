from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
from langchain_core.documents import Document

from config import MONGODB_URI

client = AsyncIOMotorClient(MONGODB_URI)

db = client.github_rag

chunks_collection = db.chunks

repositories_collection = db.repositories

query_logs_collection = db.query_logs

evaluations_collection = db.evaluations


# -----------------------------
# STORE CHUNKS TO MONGODB
# -----------------------------
async def store_chunks_metadata(
    chunks: list[Document],
    repo_name: str,
    user_id: str,
):
    """
    Persist full chunk metadata + page_content to MongoDB.
    Uses deterministic _id so re-ingestion is an idempotent upsert.
    """
    namespace = f"{user_id[:8]}_{repo_name}"

    # Delete old chunks for this namespace before re-ingesting
    await chunks_collection.delete_many({"namespace": namespace})

    if not chunks:
        return

    ops = []
    for i, chunk in enumerate(chunks):
        doc_id = f"{namespace}_chunk_{i}"

        record = {
            "namespace": namespace,
            "repo": repo_name,
            "user_id": user_id,
            "chunk_index": i,
            "page_content": chunk.page_content,
            # Store all metadata fields
            "file_path": chunk.metadata.get("file_path", ""),
            "extension": chunk.metadata.get("extension", ""),
            "language": chunk.metadata.get("language", ""),
            "chunk_type": chunk.metadata.get("chunk_type", ""),
            "symbol_name": chunk.metadata.get("symbol_name", ""),
            "start_line": chunk.metadata.get("start_line", 0),
            "end_line": chunk.metadata.get("end_line", 0),
            "imports": chunk.metadata.get("imports", []),
        }

        ops.append(
            UpdateOne(
                {"_id": doc_id},
                {"$set": record},
                upsert=True,
            )
        )

    result = await chunks_collection.bulk_write(ops)
    print(
        f"MongoDB: stored {result.upserted_count + result.modified_count} "
        f"chunks for namespace '{namespace}'"
    )


# -----------------------------
# LOAD CHUNKS FROM MONGODB
# -----------------------------
async def load_chunks_for_repo(
    repo_name: str,
    user_id: str,
) -> list[Document]:
    """
    Retrieve all stored chunks for a repo as LangChain Documents.
    Used at query time to build the BM25 retriever.
    """
    namespace = f"{user_id[:8]}_{repo_name}"

    documents: list[Document] = []

    cursor = chunks_collection.find(
        {"namespace": namespace}
    ).sort("chunk_index", 1)

    async for record in cursor:
        metadata = {
            "repo": record.get("repo", ""),
            "file_path": record.get("file_path", ""),
            "extension": record.get("extension", ""),
            "language": record.get("language", ""),
            "chunk_type": record.get("chunk_type", ""),
            "symbol_name": record.get("symbol_name", ""),
            "start_line": record.get("start_line", 0),
            "end_line": record.get("end_line", 0),
            "imports": record.get("imports", []),
            "chunk_index": record.get("chunk_index", 0),
        }

        documents.append(
            Document(
                page_content=record.get("page_content", ""),
                metadata=metadata,
            )
        )

    print(
        f"MongoDB: loaded {len(documents)} chunks "
        f"for namespace '{namespace}'"
    )

    return documents