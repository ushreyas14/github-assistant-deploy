# Pydantic Usage in This Project

This document lists all code that uses Pydantic and explains its role in the project.

## 1) Request Models (Pydantic BaseModel)

Source: backend/schemas/models.py

```python
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
```

Explanation:
- Defines the JSON schema for incoming API requests.
- `IngestRequest` validates the repo URL input for the ingest endpoint.
- `QueryRequest` validates question/query inputs and uses `Field` to constrain `top_k` between 1 and 20 with a default of 8.
- `SignupRequest` and `LoginRequest` validate auth credentials.

## 2) Ingest Endpoint Uses Pydantic Model

Source: backend/routers/ingest.py

```python
from backend.schemas.models import IngestRequest

@router.post('/ingest')
def ingest(req: IngestRequest, auth: AuthContext = Depends(get_auth_context)):
    ...
```

Explanation:
- FastAPI uses `IngestRequest` to parse and validate the JSON request body for `/ingest`.
- Invalid/missing fields are rejected automatically by Pydantic before the handler runs.

## 3) Query Endpoint Uses Pydantic Model

Source: backend/routers/query.py

```python
from backend.schemas.models import QueryRequest

@router.post("/")
def query_repo(req: QueryRequest, auth: AuthContext = Depends(get_auth_context)):
    ...
```

Explanation:
- FastAPI uses `QueryRequest` to validate search queries.
- Pydantic enforces `top_k` bounds (1 to 20) and provides a default if omitted.

## 4) Auth Endpoints Use Pydantic Models

Source: backend/routers/auth.py

```python
from backend.schemas.models import SignupRequest, LoginRequest

@router.post("/signup")
def signup(req: SignupRequest):
    ...

@router.post("/login")
def login(req: LoginRequest):
    ...
```

Explanation:
- `SignupRequest` and `LoginRequest` ensure the request body contains required `email` and `password` fields.
- Pydantic validation runs before the handler logic, simplifying error handling and input sanitation.
