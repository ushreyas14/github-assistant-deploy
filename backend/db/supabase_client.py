from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_ANON_KEY

def get_client(access_token: str | None = None) -> Client:
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    if access_token:
        # Attach the user's JWT so Postgres RLS can evaluate auth.uid().
        client.postgrest.auth(access_token)
    return client

def get_authenticated_user(access_token: str):
    return get_client().auth.get_user(access_token).user

def sign_up(email: str, password: str):
    return get_client().auth.sign_up({
        "email": email,
        "password": password
    })

def sign_in(email: str, password: str):
    return get_client().auth.sign_in_with_password({
        "email": email,
        "password": password
    })

def sign_out():
    get_client().auth.sign_out()

def save_repo(
    user_id: str,
    repo_name: str,
    repo_url: str,
    chunk_count: int,
    access_token: str | None = None,
):
    
    namespace = f"{user_id[:8]}_{repo_name}"
    get_client(access_token).table("user_repos").upsert(
        {
            "user_id": user_id,
            "repo_name": repo_name,
            "repo_url": repo_url,
            "namespace": namespace,
            "chunk_count": chunk_count,
            "status": "ready",
        },
        on_conflict="user_id,repo_name",
    ).execute()

    return namespace

def get_user_repos(user_id: str, access_token: str | None = None) -> list:
    try:
        response = (
            get_client(access_token)
            .table("user_repos")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
    except Exception as exc:
        # Backward compatibility for older schemas that don't have created_at.
        if "created_at" not in str(exc):
            raise
        response = (
            get_client(access_token)
            .table("user_repos")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
    return response.data or []

def delete_repo(user_id: str, repo_name: str, access_token: str | None = None):
    (
        get_client(access_token)
        .table("user_repos")
        .delete()
        .eq("user_id", user_id)
        .eq("repo_name", repo_name)
        .execute()
    )