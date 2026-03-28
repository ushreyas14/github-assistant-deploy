from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_ANON_KEY

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

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

def save_repo(user_id: str, repo_name: str, repo_url: str, chunk_count: int):
    
    namespace = f"{user_id[:8]}_{repo_name}"
    get_client().table("user_repos").upsert({
        "user_id": user_id,
        "repo_name": repo_name,
        "repo_url": repo_url,
        "namespace": namespace,
        "chunk_count": chunk_count,
        "status": "ready"
    }).execute()

    return namespace

def get_user_repos(user_id: str)->list:
    response = get_client().table("user_repos").select("*").eq("user_id", user_id).execute()
    return response.data

def delete_repo(user_id: str, repo_name: str):
    get_client().table("user_repos").delete().eq("user_id", user_id).eq("repo_name", repo_name).execute()