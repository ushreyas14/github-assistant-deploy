"""Validation tests for the Pydantic request models used by the API routers."""

import pytest
from pydantic import ValidationError

from backend.schemas.models import IngestRequest, LoginRequest, QueryRequest


def test_query_request_applies_default_top_k():
    req = QueryRequest(question="What does this repo do?", repo_name="my-repo")
    assert req.top_k == 8


def test_query_request_rejects_top_k_out_of_range():
    with pytest.raises(ValidationError):
        QueryRequest(question="q", repo_name="repo", top_k=21)

    with pytest.raises(ValidationError):
        QueryRequest(question="q", repo_name="repo", top_k=0)


def test_query_request_accepts_top_k_within_range():
    req = QueryRequest(question="q", repo_name="repo", top_k=20)
    assert req.top_k == 20


def test_ingest_request_requires_repo_url():
    with pytest.raises(ValidationError):
        IngestRequest()

    req = IngestRequest(repo_url="https://github.com/example/repo")
    assert req.repo_url == "https://github.com/example/repo"


def test_login_request_requires_email_and_password():
    with pytest.raises(ValidationError):
        LoginRequest(email="user@example.com")

    req = LoginRequest(email="user@example.com", password="secret")
    assert req.email == "user@example.com"
    assert req.password == "secret"
