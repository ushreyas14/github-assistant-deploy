from pydantic import BaseModel
from typing import Optional

class IngestRequest(BaseModel):
    repo_url: str
    user_id: str

class QueryRequest(BaseModel):
    question: str
    repo_name: str
    user_id: str
    top_k: Optional[int]=8

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str