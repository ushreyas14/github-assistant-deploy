import os
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    GROQ_API_KEY     = st.secrets.get("GROQ_API_KEY")     or os.getenv("GROQ_API_KEY")
    PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY") or os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX   = st.secrets.get("PINECONE_INDEX_NAME") or os.getenv("PINECONE_INDEX_NAME", "github-rag")
except:
    GROQ_API_KEY     = os.getenv("GROQ_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX   = os.getenv("PINECONE_INDEX_NAME", "github-rag")

# Rest of config stays the same
GROQ_MODEL  = "llama-3.3-70b-versatile"
EMBED_MODEL = "all-MiniLM-L6-v2"
EMBED_DIM   = 384
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 150
TOP_K         = 8

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".md", ".txt",
    ".yaml", ".yml", ".json", ".html", ".sh"
}

IGNORED_DIRS = {
    ".git", "node_modules", "__pycache__",
    ".venv", "dist", "build"   
    #HELLO
}

