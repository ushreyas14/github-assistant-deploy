from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from chain.embeddings import get_embeddings
from config import PINECONE_API_KEY, PINECONE_INDEX, EMBED_DIM
import time

import vectorstore
def get_pinecone_client()->Pinecone:
    return Pinecone(api_key=PINECONE_API_KEY)

def create_index_if_not_exists(pc: Pinecone):
    existing = [i.name for i in pc.list_indexes()]

    if PINECONE_INDEX not in existing:
        print(f"Creating index '{PINECONE_INDEX}'...")
        pc.create_index(
            name = PINECONE_INDEX,
            dimension = EMBED_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        while not pc.describe_index(PINECONE_INDEX).status["ready"]:
            print("Waiting for index to be ready...")
            time.sleep(5)
        print("Index is ready!")
    else:
        print(f"Index '{PINECONE_INDEX}' already exists.")

def ingest_to_pinecone(chunks, repo_name: str, user_id: str) -> PineconeVectorStore:
    namespace = f"{user_id[:8]}_{repo_name}"
    pc = get_pinecone_client()
    embeddings = get_embeddings()

    create_index_if_not_exists(pc)

    # -----------------------------------------------------------
    # Trim metadata for Pinecone (full metadata lives in MongoDB)
    # -----------------------------------------------------------
    MAX_TEXT_BYTES = 36_000  # stay well under Pinecone's 40KB limit

    pinecone_chunks = []
    for chunk in chunks:
        trimmed_meta = {
            "repo": chunk.metadata.get("repo", ""),
            "file_path": chunk.metadata.get("file_path", ""),
            "symbol_name": chunk.metadata.get("symbol_name", ""),
            "chunk_type": chunk.metadata.get("chunk_type", ""),
            "chunk_index": chunk.metadata.get("chunk_index", 0),
        }

        content = chunk.page_content
        if len(content.encode("utf-8")) > MAX_TEXT_BYTES:
            # Truncate to stay under the limit (Pinecone stores
            # page_content inside metadata as the 'text' key)
            content = content[:MAX_TEXT_BYTES]

        pinecone_chunks.append(
            Document(page_content=content, metadata=trimmed_meta)
        )

    print(f"Upserting {len(pinecone_chunks)} chunks into namespace '{namespace}'...")
    vectorstore = PineconeVectorStore.from_documents(
        documents = pinecone_chunks,
        embedding = embeddings,
        index_name = PINECONE_INDEX,
        namespace = namespace,
    )

    print("Upsert complete!")
    return vectorstore

def load_vectorstore(repo_name: str, user_id: str)->PineconeVectorStore:
    namespace = f"{user_id[:8]}_{repo_name}"
    return PineconeVectorStore(
        index_name      = PINECONE_INDEX,
        embedding       = get_embeddings(),
        namespace       = namespace,
        pinecone_api_key = PINECONE_API_KEY
    )