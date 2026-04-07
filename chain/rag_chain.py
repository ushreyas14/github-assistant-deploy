from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from config import GROQ_API_KEY, GROQ_MODEL, TOP_K

SYSTEM_PROMPT = """You are an expert software engineering assistant 
analyzing a GitHub repository.

Answer questions using ONLY the provided code context. Rules:
1. Always cite the file path (e.g. "In `src/flask/app.py`...")
2. Include relevant code snippets from the context
3. If the answer isn't in the context say "I couldn't find that in the indexed files"
4. Be precise and technical, never guess

Context from the repository:
{context}"""

def format_docs(docs) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content
        parts.append(f"--- [{i}] {source} ---\n{content}")
        
    return "\n\n".join(parts)

def build_rag_chain(vectorstore: PineconeVectorStore, top_k: int | None = None):

    k = top_k or TOP_K

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

    llm = ChatGroq(
        api_key = GROQ_API_KEY,
        model = GROQ_MODEL,
        temperature = 0.1, 
        streaming = True
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])

    chain = (
        {
            "context":  retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever