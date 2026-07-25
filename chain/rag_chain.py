from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate

from langchain_pinecone import PineconeVectorStore

from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda
)

from langchain_core.output_parsers import StrOutputParser

from langchain_community.retrievers import BM25Retriever

from langchain.retrievers import EnsembleRetriever

from sentence_transformers import CrossEncoder


from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    TOP_K
)


# -----------------------------
# RERANKER MODEL
# -----------------------------
reranker = CrossEncoder(
    "BAAI/bge-reranker-base"
)


SYSTEM_PROMPT = """
You are an expert software engineering assistant 
analyzing a GitHub repository.

Answer questions using ONLY the provided code context.

Rules:
1. Always cite the file path
2. Include relevant code snippets
3. If answer not found say:
   "I couldn't find that in the indexed files"
4. Be precise and technical
5. Never hallucinate repository structure

Context:
{context}
"""


# -----------------------------
# FORMAT RETRIEVED DOCS
# -----------------------------
def format_docs(docs) -> str:

    parts = []

    for i, doc in enumerate(docs, 1):

        source = (
            doc.metadata.get("file_path")
            or doc.metadata.get("source", "unknown")
        )

        symbol = doc.metadata.get(
            "symbol_name",
            ""
        )

        chunk_type = doc.metadata.get(
            "chunk_type",
            ""
        )

        content = doc.page_content

        header = (
            f"--- [{i}] {source}"
        )

        if symbol:
            header += f" | Symbol: {symbol}"

        if chunk_type:
            header += f" | Type: {chunk_type}"

        header += " ---"

        parts.append(
            f"{header}\n{content}"
        )

    return "\n\n".join(parts)


# -----------------------------
# CROSS-ENCODER RERANKING
# -----------------------------
def rerank_documents(
    query,
    docs,
    top_n=8,
    score_threshold: float = -5.0,
):
    """Rerank docs with CrossEncoder. Falls back to original order if reranker
    produces no results above score_threshold or raises an error."""

    if not docs:
        return []

    try:
        pairs = [
            (query, doc.page_content)
            for doc in docs
        ]

        scores = reranker.predict(pairs)

        scored_docs = sorted(
            zip(docs, scores),
            key=lambda x: x[1],
            reverse=True
        )

        print("\n========== RERANK RESULTS ==========")
        reranked_docs = []
        for doc, score in scored_docs[:top_n]:
            source = doc.metadata.get("file_path", "unknown")
            symbol = doc.metadata.get("symbol_name", "")
            print(f"Score: {score:.4f} | {source} | {symbol}")
            if score >= score_threshold:
                reranked_docs.append(doc)
        print("====================================\n")

        # Fallback: if threshold filtered everything, return top_n without filter
        if not reranked_docs:
            print("[rerank] All scores below threshold — returning top_n unfiltered")
            reranked_docs = [doc for doc, _ in scored_docs[:top_n]]

        return reranked_docs

    except Exception as e:
        print(f"[rerank] Reranker failed ({e}), falling back to retrieval order")
        return docs[:top_n]


# -----------------------------
# BUILD RAG CHAIN
# -----------------------------
def build_rag_chain(
    vectorstore: PineconeVectorStore,
    documents,
    top_k: int | None = None
):

    # Retrieve more initially
    k = top_k or TOP_K

    # -----------------------------
    # VECTOR RETRIEVER
    # -----------------------------
    vector_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

    # -----------------------------
    # BM25 RETRIEVER
    # -----------------------------
    bm25_retriever = BM25Retriever.from_documents(
        documents
    )

    bm25_retriever.k = k

    # -----------------------------
    # HYBRID RETRIEVER
    # -----------------------------
    retriever = EnsembleRetriever(
        retrievers=[
            bm25_retriever,
            vector_retriever
        ],

        # BM25, Vector
        weights=[0.4, 0.6]
    )

    # -----------------------------
    # RETRIEVE + RERANK
    # -----------------------------
    # Store last reranked docs so query.py can return them as sources
    _last_reranked: list = []

    def retrieve_and_rerank(query: str):
        nonlocal _last_reranked

        print(f"\nQuery: {query}")

        # Initial retrieval
        docs = retriever.invoke(query)
        print(f"Retrieved {len(docs)} docs before reranking")

        # Rerank
        reranked_docs = rerank_documents(
            query=query,
            docs=docs,
        )

        _last_reranked = reranked_docs

        # Final formatting
        return format_docs(reranked_docs)

    def get_last_reranked() -> list:
        return _last_reranked

    # -----------------------------
    # LLM
    # -----------------------------
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0.1,
        streaming=True
    )

    # -----------------------------
    # PROMPT
    # -----------------------------
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])

    # -----------------------------
    # FINAL CHAIN
    # -----------------------------
    chain = (
        {
            "context":
                RunnableLambda(
                    retrieve_and_rerank
                ),

            "question":
                RunnablePassthrough()
        }

        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, get_last_reranked