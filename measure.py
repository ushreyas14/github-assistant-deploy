import os
import time

# Force unbuffered stdout just in case
import sys

def measure():
    print("Loading modules...", flush=True)
    from ingestion.cloner import clone_or_pull
    from ingestion.loader import load_repo_documents
    from ingestion.chunker import chunk_documents
    from vectorstore.pinecone_store import ingest_to_pinecone, load_vectorstore
    from chain.rag_chain import build_rag_chain

    repo_url = 'https://github.com/pallets/flask'
    user_id = 'testuser-flask-1'

    # 1. Clone
    print("Cloning repository...", flush=True)
    t0 = time.time()
    path, name = clone_or_pull(repo_url)
    t1 = time.time()
    print(f"Clone Time: {t1-t0:.2f}s", flush=True)

    # Count LOC naively for context
    docs_list = load_repo_documents(path)
    total_lines = 0
    for docs in docs_list:
        if hasattr(docs, 'page_content'):
            total_lines += len(docs.page_content.splitlines())
    print(f"Approximate Lines of Code (indexed): {total_lines}", flush=True)

    # 2. Load & Chunk
    print("Chunking documents...", flush=True)
    t2 = time.time()
    chunks = chunk_documents(docs_list)
    t3 = time.time()
    print(f"Load & Chunk Time: {t3-t2:.2f}s, generated {len(chunks)} chunks.", flush=True)

    # 3. Ingest
    print("Ingesting to Pinecone...", flush=True)
    t4 = time.time()
    vs = ingest_to_pinecone(chunks, name, user_id)
    t5 = time.time()
    print(f"Pinecone Ingestion Time: {t5-t4:.2f}s", flush=True)

    # 4. Query
    print("Setting up query chain...", flush=True)
    t6 = time.time()
    vs = load_vectorstore(name, user_id)
    chain, retriever = build_rag_chain(vs)
    question = 'How does Flask handle URL routing?'

    print("Sending Query...", flush=True)
    ans = ''
    t_start_query = time.time()
    try:
        for chunk in chain.stream(question):
            ans += str(chunk)
    except Exception as e:
        print(f"Query failed: {e}", flush=True)
    t7 = time.time()
    print(f"\nQuery Retrieval & Generation Time: {t7-t_start_query:.2f}s", flush=True)

if __name__ == '__main__':
    measure()
