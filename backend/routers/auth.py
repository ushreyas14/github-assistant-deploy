from fastapi import APIRouter, HTTPException
from backend.schemas.models import SignupRequest, LoginRequest
from backend.db.supabase_client import sign_in, sign_up, sign_out

router = APIRouter()


def _friendly_auth_error(op: str, err: Exception) -> tuple[int, str]:
    raw = str(err).lower()

    if op == "signup":
        if "already" in raw and "register" in raw:
            return 409, "Account already exists. Please sign in instead."
        return 400, "Unable to create account. Please check your details and try again."

    if op == "login":
        if "invalid login credentials" in raw:
            return 401, "Invalid email or password."
        if "email not confirmed" in raw:
            return 401, "Please confirm your email before signing in."
        return 400, "Unable to sign in right now. Please try again."

    return 400, "Authentication failed."

@router.post("/signup")
def signup(req: SignupRequest):
    try:
        response = sign_up(req.email, req.password)
        return {"message": "success", "user": response.user.email}
    except Exception as e:
        status, detail = _friendly_auth_error("signup", e)
        raise HTTPException(status_code=status, detail=detail)

@router.post("/login")
def login(req: LoginRequest):
    try:
        response = sign_in(req.email, req.password)
        return {"message": "success", "user": response.session.access_token}
    except Exception as e:
        status, detail = _friendly_auth_error("login", e)
        raise HTTPException(status_code=status, detail=detail)

@router.post('/logout')
def logout():
    try:
        sign_out()
        return {"message": "logged out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))