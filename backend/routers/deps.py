from dataclasses import dataclass

from fastapi import Header, HTTPException

from backend.db.supabase_client import get_authenticated_user


@dataclass
class AuthContext:
    user_id: str
    access_token: str


def get_auth_context(authorization: str = Header(default="")) -> AuthContext:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    try:
        user = get_authenticated_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return AuthContext(user_id=str(user.id), access_token=token)
