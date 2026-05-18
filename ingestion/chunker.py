from tree_sitter_language_pack import get_parser
from langchain_core.documents import Document
from langchain_text_splitters import (RecursiveCharacterTextSplitter, Language)
from config import (CHUNK_SIZE, CHUNK_OVERLAP)

LANGUAGE_MAP = {
    ".py": "python", 
    ".js": "javascript", 
    ".jsx": "javascript",
    ".ts": "typescript", 
    ".tsx": "typescript"
}

SPLITTER_LANGUAGE_MAP = {
    ".md": Language.MARKDOWN,
    ".html": Language.HTML
}

CHUNK_NODE_TYPES = {

    "python": {
        "function_definition",
        "class_definition",
    },

    "javascript": {
        "function_declaration",
        "class_declaration",
        "method_definition",
    },

    "typescript": {
        "function_declaration",
        "class_declaration",
        "method_definition",
    }
}

def get_recursive_splitter(ext: str):
    
    if ext in SPLITTER_LANGUAGE_MAP:

        return RecursiveCharacterTextSplitter.from_language(
            language=SPLITTER_LANGUAGE_MAP[ext], 
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
    
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )

def extract_node_name(node, code_bytes):
    name_node = node.child_by_field_name("name")
    
    if not name_node:
        return "anonymous"
    
    return code_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8")

def treesitter_chunk_document(doc: Document):

    ext = doc.metadata.get("extension", "")

    if ext not in LANGUAGE_MAP:
        return []

    language = LANGUAGE_MAP[ext]
    parser = get_parser(language)

    code = doc.page_content
    code_bytes = code.encode("utf-8")
    
    tree = parser.parse(code_bytes)
    root = tree.root_node

    target_types = CHUNK_NODE_TYPES[language]

    chunks = []
    stack = [root]

    while stack:

        node = stack.pop()

        if node.type in target_types:

            chunk_code = code_bytes[node.start_byte:node.end_byte].decode("utf-8")
            symbol_name = extract_node_name(node,code_bytes)

            metadata = {
                **doc.metadata,
                "language": language,
                "chunk_type": node.type,
                "symbol_name": symbol_name,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
            }

            chunks.append(
                Document(
                    page_content=chunk_code,
                    metadata=metadata
                )
            )

        stack.extend(node.children)

    return chunks


def recursive_chunk_document(doc: Document):

    ext = doc.metadata.get("extension", "")
    splitter = get_recursive_splitter(ext)
    chunks = splitter.split_documents([doc])

    return chunks


def chunk_documents(docs: list[Document]):

    all_chunks = []

    for doc in docs:
        ext = doc.metadata.get("extension", "")

        if ext in LANGUAGE_MAP:
            chunks = treesitter_chunk_document(doc)

            if not chunks:
                chunks = recursive_chunk_document(doc)

        else:
            chunks = recursive_chunk_document(doc)

        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i

        all_chunks.extend(chunks)

    print(f"Total chunks: {len(all_chunks)}")

    return all_chunks