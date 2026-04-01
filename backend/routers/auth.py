from fastapi import APIRouter
from backend.schemas.models import SignupRequest, LoginRequest
from backend.db.supabase_client import sign_in, sign_up, sign_out

router = APIRouter()

@router.post("/signup")
def signup(req: SignupRequest):
    response = sign_up(req.email, req.password)
    return {"message": "success", "user": response.user.email}

@router.post("/login")
def login(req: LoginRequest):
    response = sign_in(req.email, req.password)
    return {"message": "success", "user": response.session.access_token}

@router.post('/logut')
def logout():
    sign_out()
    return {"message": "logged out"}