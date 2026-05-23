import os
from pathlib import Path
from langchain_core.documents import Document
from config import SUPPORTED_EXTENSIONS, IGNORED_DIRS

def load_repo_documents(repo_path: str) -> list[Document]:
    docs      = []
    repo_root = Path(repo_path)
    repo_name = repo_root.name

    for root, dirs, files in os.walk(repo_path):

        # Skip ignored folders like node_modules, .git etc
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for filename in files:
            filepath = Path(root) / filename

            # Skip unsupported file types
            if filepath.suffix not in SUPPORTED_EXTENSIONS:
                continue

            # Read the file
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                print(f"Skipping {filepath}: {e}")
                continue

            # Skip empty files
            if not content.strip():
                continue

            relative_path = str(filepath.relative_to(repo_root))

            # Prepend file path as a header — helps LLM know where code lives
            full_content = f"# File: {relative_path}\n\n{content}"

            doc = Document(
                page_content=full_content,
                metadata={
                    "repo": repo_name,
                    "file_path": relative_path,
                    "extension": filepath.suffix,
                }
            )
            docs.append(doc)

    print(f"Loaded {len(docs)} files from {repo_name}")
    return docs