from tree_sitter_language_pack import get_parser
from langchain_core.documents import Document
from langchain_text_splitters import (RecursiveCharacterTextSplitter, Language)
from config import (CHUNK_SIZE, CHUNK_OVERLAP)
import ast
import re

LANGUAGE_MAP = {
    ".py": "python", 
    ".js": "javascript", 
    ".jsx": "javascript",
    ".ts": "typescript", 
    ".tsx": "typescript"
}

FALLBACK_LANGUAGE_BY_EXT = {
    ".md": "markdown",
    ".html": "html",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".sh": "shell",
    ".txt": "text",
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


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if not item:
            continue
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def extract_imports(language: str, code: str) -> list[str]:
    """Extract a small, metadata-friendly list of imported module names."""

    if not code:
        return []

    if language == "python":
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name or "").split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])

        return _dedupe_preserve_order(imports)

    if language in {"javascript", "typescript"}:
        modules: list[str] = []
        modules.extend(re.findall(r"\\bimport\\s+[^;]*?from\\s+['\"]([^'\"]+)['\"]", code))
        modules.extend(re.findall(r"\\brequire\\(\\s*['\"]([^'\"]+)['\"]\\s*\\)", code))

        normalized: list[str] = []
        for mod in modules:
            if not mod:
                continue
            # Trim relative prefixes and split on path.
            while mod.startswith("../"):
                mod = mod[3:]
            if mod.startswith("./"):
                mod = mod[2:]
            mod = mod.lstrip("/")
            mod = mod.split("/")[0]
            if mod:
                normalized.append(mod)

        return _dedupe_preserve_order(normalized)

    return []

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

    start_byte = _get_attr_or_call(name_node, "start_byte")
    end_byte = _get_attr_or_call(name_node, "end_byte")
    return code_bytes[start_byte:end_byte].decode("utf-8")


def _get_attr_or_call(obj, attr: str, default=None):
    if not hasattr(obj, attr):
        return default
    value = getattr(obj, attr)
    return value() if callable(value) else value


def _node_kind(node) -> str:
    # tree-sitter node kind is exposed as `type` (property) in some bindings,
    # and as `kind()` in others (e.g., tree_sitter_language_pack).
    return (
        _get_attr_or_call(node, "type")
        or _get_attr_or_call(node, "kind")
        or ""
    )


def _node_children(node):
    children = _get_attr_or_call(node, "children")
    if children is not None:
        return children

    child_count = _get_attr_or_call(node, "child_count")
    child_fn = getattr(node, "child", None)
    if child_count is None or not callable(child_fn):
        return []

    return [child_fn(i) for i in range(child_count)]


def _pos_row(pos) -> int | None:
    if pos is None:
        return None
    if isinstance(pos, (tuple, list)) and len(pos) >= 1:
        return int(pos[0])
    row = _get_attr_or_call(pos, "row")
    return int(row) if row is not None else None


def _node_start_end_lines(node) -> tuple[int | None, int | None]:
    start = _get_attr_or_call(node, "start_point")
    if start is None:
        start = _get_attr_or_call(node, "start_position")
    end = _get_attr_or_call(node, "end_point")
    if end is None:
        end = _get_attr_or_call(node, "end_position")

    start_row = _pos_row(start)
    end_row = _pos_row(end)
    start_line = start_row + 1 if start_row is not None else None
    end_line = end_row + 1 if end_row is not None else None
    return start_line, end_line

def treesitter_chunk_document(doc: Document):

    ext = doc.metadata.get("extension", "")

    if ext not in LANGUAGE_MAP:
        return []

    language = LANGUAGE_MAP[ext]
    parser = get_parser(language)

    code = doc.page_content
    code_bytes = code.encode("utf-8")

    file_path = doc.metadata.get("file_path") or doc.metadata.get("source")
    base_metadata = {
        "repo": doc.metadata.get("repo"),
        "file_path": file_path,
        "extension": ext,
        "language": language,
    }

    file_imports = extract_imports(language, code)

    # tree-sitter python bindings differ by version/package:
    # some expect `bytes` (UTF-8), others accept `str`.
    try:
        tree = parser.parse(code_bytes)
    except TypeError:
        tree = parser.parse(code)
    root = _get_attr_or_call(tree, "root_node")

    target_types = CHUNK_NODE_TYPES[language]

    chunks = []
    stack = [root]

    while stack:

        node = stack.pop()

        node_kind = _node_kind(node)

        if node_kind in target_types:

            start_byte = _get_attr_or_call(node, "start_byte")
            end_byte = _get_attr_or_call(node, "end_byte")
            if start_byte is None or end_byte is None:
                stack.extend(_node_children(node))
                continue

            chunk_code = code_bytes[start_byte:end_byte].decode("utf-8")
            symbol_name = extract_node_name(node,code_bytes)

            start_line, end_line = _node_start_end_lines(node)

            metadata = {
                **base_metadata,
                "chunk_type": node_kind,
                "symbol_name": symbol_name,
                "start_line": start_line or 0,
                "end_line": end_line or 0,
                "imports": file_imports,
            }

            node_doc = Document(
                page_content=chunk_code,
                metadata=metadata
            )

            # Pinecone enforces a 40KB metadata limit per vector.
            # LangChain's Pinecone integration stores the document text inside metadata
            # (default text_key), so very large AST nodes (big classes/functions) can blow
            # past the limit. Cap/split oversized nodes here.
            if len(chunk_code) > CHUNK_SIZE:
                splitter = get_recursive_splitter(ext)
                chunks.extend(splitter.split_documents([node_doc]))
            else:
                chunks.append(node_doc)

        stack.extend(_node_children(node))

    return chunks


def recursive_chunk_document(doc: Document):

    ext = doc.metadata.get("extension", "")
    splitter = get_recursive_splitter(ext)

    language = LANGUAGE_MAP.get(ext) or FALLBACK_LANGUAGE_BY_EXT.get(ext) or "text"

    code = doc.page_content
    file_path = doc.metadata.get("file_path") or doc.metadata.get("source")

    metadata = {
        "repo": doc.metadata.get("repo"),
        "file_path": file_path,
        "extension": ext,
        "language": language,
        "chunk_type": "recursive",
        "symbol_name": "",
        "start_line": 0,
        "end_line": 0,
        "imports": extract_imports(language or "", code),
    }

    base_doc = Document(page_content=code, metadata=metadata)
    return splitter.split_documents([base_doc])


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