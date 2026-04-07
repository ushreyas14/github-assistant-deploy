from pydantic import BaseModel, Field
from typing import Optional

class IngestRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    question: str
    repo_name: str
    top_k: Optional[int] = Field(default=8, ge=1, le=20)

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str