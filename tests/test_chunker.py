"""Unit tests for the pure-logic helpers in ingestion/chunker.py.

These exercise import extraction and de-duplication only - no tree-sitter
parsing, network calls, or model downloads are involved.
"""

from ingestion.chunker import _dedupe_preserve_order, extract_imports


def test_dedupe_preserve_order_removes_duplicates_and_empties():
    items = ["os", "sys", "os", "", "re", "sys", None]
    assert _dedupe_preserve_order(items) == ["os", "sys", "re"]


def test_extract_imports_python_handles_import_and_from():
    code = (
        "import os\n"
        "import sys as _sys\n"
        "from collections import OrderedDict\n"
        "from . import sibling\n"
    )
    assert extract_imports("python", code) == ["os", "sys", "collections"]


def test_extract_imports_python_ignores_invalid_syntax():
    assert extract_imports("python", "def broken(:") == []


def test_extract_imports_javascript_handles_import_and_require():
    code = (
        "import React from 'react';\n"
        "import { useState } from \"react-dom/client\";\n"
        "const path = require('node:path');\n"
        "import './styles.css';\n"
    )
    assert extract_imports("javascript", code) == [
        "react",
        "react-dom",
        "node:path",
    ]


def test_extract_imports_unknown_language_returns_empty_list():
    assert extract_imports("rust", "use std::io;") == []


def test_extract_imports_empty_code_returns_empty_list():
    assert extract_imports("python", "") == []
