---
title: GitHub Assistant API
emoji: 🤖
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
---

# GitHub RAG Agent


A Retrieval-Augmented Generation (RAG) agent that indexes GitHub repositories and lets you ask natural language questions about the codebase. It clones repos, chunks source files with language-aware splitters, stores embeddings in Pinecone, and answers queries using Groq LLMs.

## Features

- **Repo Cloning** — Clone any public GitHub repo (or pull latest if already cloned)
- **Smart File Loading** — Loads supported file types (`.py`, `.js`, `.ts`, `.md`, `.html`, `.yaml`, `.json`, `.sh`, `.txt`) while skipping noise directories (`.git`, `node_modules`, `__pycache__`, etc.)
- **Language-Aware Chunking** — Uses LangChain's `RecursiveCharacterTextSplitter` with language-specific separators for Python, JavaScript, TypeScript, Markdown, and HTML
- **Vector Storage** — Embeds chunks and upserts them into a Pinecone index for fast similarity search
- **LLM Q&A** — Retrieves relevant chunks and generates answers via Groq

## Project Structure

```
github-agent/
├── main.py                 # Entry point
├── config.py               # Supported extensions, ignored dirs, chunk settings
├── ingestion/
│   ├── cloner.py           # Git clone / pull logic
│   ├── loader.py           # Walk repo and create LangChain Documents
│   └── chunker.py          # Language-aware text splitting
├── chain/
│   └── embeddings.py       # Embedding + LLM chain (WIP)
├── vectorstore/            # Pinecone vector store integration (WIP)
├── ui/                     # Frontend / UI (WIP)
├── repos/                  # Cloned repositories (git-ignored)
└── .env                    # API keys (not committed)
```

## Prerequisites

- Python 3.10+
- A [Groq](https://console.groq.com/) API key
- A [Pinecone](https://www.pinecone.io/) API key and index

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/github-agent.git
   cd github-agent
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example env file and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env`:
   ```
   GROQ_API_KEY=your_groq_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=github-rag
   ```

## Usage

```bash
python main.py
```

By default this clones the [Flask](https://github.com/pallets/flask) repository, loads its source files, and chunks them. You can modify the repo URL in `main.py` to index any public GitHub repository.

## Configuration

Edit [`config.py`](config.py) to customise:

| Setting | Default | Description |
|---|---|---|
| `SUPPORTED_EXTENSIONS` | `.py`, `.js`, `.ts`, `.md`, `.txt`, `.yaml`, `.yml`, `.json`, `.html`, `.sh` | File types to index |
| `IGNORED_DIRS` | `.git`, `node_modules`, `__pycache__`, `.venv`, `dist`, `build` | Directories to skip |
| `CHUNK_SIZE` | 1000 | Maximum characters per chunk |
| `CHUNK_OVERLAP` | 150 | Overlap between consecutive chunks |

## Tech Stack

- [LangChain](https://python.langchain.com/) — Document loading, text splitting, and chain orchestration
- [Pinecone](https://www.pinecone.io/) — Vector database for storing and querying embeddings
- [Groq](https://groq.com/) — Fast LLM inference
- [GitPython](https://gitpython.readthedocs.io/) — Git operations from Python

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
