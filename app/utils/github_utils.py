import httpx
from fastapi import HTTPException
from ..config import supabase

def get_github_token(user_id: str):
    """Get GitHub access token for a user from the database"""
    github_token = supabase.table('users').select('github_access_token').eq('id', user_id).maybe_single().execute().data
    
    if not github_token or not github_token['github_access_token']:
        return None
    
    return github_token['github_access_token']

def validate_github_token(token: str, required_scopes: set = None):
    """
    Validate GitHub token and check if it has required scopes.
    Returns user info if valid, raises HTTPException otherwise.
    """
    if not token:
        raise HTTPException(status_code=400, detail="GitHub token not found")
    
    # Check if token is valid by making a request to GitHub API
    user_info_response = httpx.get("https://api.github.com/user", headers={
        "Authorization": f"Bearer {token}"
    })
    
    if user_info_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid GitHub token")
    
    # If required scopes are provided, check them
    if required_scopes:
        scopes = [scope.strip() for scope in user_info_response.headers.get('X-OAuth-Scopes', '').split(',')]
        missing_scopes = required_scopes - set(scopes)
        
        if missing_scopes:
            raise HTTPException(
                status_code=403,
                detail=f"GitHub token has insufficient permissions. Missing scopes: {', '.join(missing_scopes)}"
            )
    
    return user_info_response.json() 