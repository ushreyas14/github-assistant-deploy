from fastapi import APIRouter, Depends, HTTPException

from backend.db.supabase_client import delete_repo, get_user_repos
from backend.routers.deps import AuthContext, get_auth_context

router = APIRouter()


@router.get("/")
def list_repos(auth: AuthContext = Depends(get_auth_context)):
    try:
        repos = get_user_repos(auth.user_id, access_token=auth.access_token)
        return {"repos": repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{repo_name}")
def remove_repo(repo_name: str, auth: AuthContext = Depends(get_auth_context)):
    try:
        delete_repo(auth.user_id, repo_name, access_token=auth.access_token)
        return {"status": "deleted", "repo_name": repo_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
