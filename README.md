---
title: GitHub Assistant
emoji: 🤖
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
---

# 🤖 GitHub Assistant

**Live Webpage:** [https://github-assistant-deploy-by4c.vercel.app/dashboard](https://github-assistant-deploy-by4c.vercel.app/dashboard)

A full-stack web application featuring a Retrieval-Augmented Generation (RAG) agent that indexes GitHub repositories and allows you to ask natural language questions about the codebase. 

With a sleek dashboard interface, users can log in, submit a GitHub repository URL to be cloned and indexed, and then interact with an AI assistant to get context-aware explanations, code snippets, and answers about the repository's structure and logic.

## ✨ Features

- **Aesthetic Dashboard UI** — Built with React + Vite, designed for a smooth and intuitive user experience.
- **Secure Authentication** — User authentication and session management powered by Supabase.
- **Automated Repo Ingestion** — Clones public repositories, filters out noise (like `.git`, `node_modules`), and extracts relevant source files.
- **Language-Aware Chunking** — Uses LangChain's `RecursiveCharacterTextSplitter` with language-specific separators for Python, JavaScript, TypeScript, Markdown, HTML, etc.
- **Vector Storage & Fast Retrieval** — Embeds code chunks using `sentence-transformers` and upserts them into a **Pinecone** index for high-speed similarity searches.
- **Lightning-Fast LLM Q&A** — Retrieves relevant code chunks and generates precise, context-aware answers via **Groq** APIs.
- **Markdown & Syntax Highlighting** — Chat responses are formatted with markdown and code syntax highlighting.

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 18, Vite
- **Routing:** React Router DOM
- **UI Components:** React Markdown, Highlight.js
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI, Python
- **Database / Auth:** Supabase
- **AI / LLM Orchestration:** LangChain
- **LLM Provider:** Groq
- **Embeddings:** `sentence-transformers` (Hugging Face)
- **Vector Database:** Pinecone
- **Git Operations:** GitPython

## 📂 Project Structure

```
github-assistant/
├── backend/                # FastAPI backend & Supabase integration
│   ├── routers/            # API Endpoints (Auth, Ingestion, Chat)
│   ├── schemas/            # Pydantic models
├── chain/                  # LangChain retrieval & QA chains
├── frontend/               # React + Vite web application
├── ingestion/              # Repository cloning, loading, and chunking logic
├── vectorstore/            # Pinecone integration and embedding utilities
├── main.py                 # FastAPI application entry point
├── config.py               # Ingestion & chunking configuration
├── requirements.txt        # Python dependencies
└── package.json            # (inside frontend/) React dependencies
```

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.10+
- Node.js (v18+)
- [Groq](https://console.groq.com/) API key
- [Pinecone](https://www.pinecone.io/) API key & index
- [Supabase](https://supabase.com/) project URL & Anon Key

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/github-assistant.git
cd github-assistant

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```ini
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=github-rag
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

Run the backend server:
```bash
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
