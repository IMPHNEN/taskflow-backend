from fastapi import APIRouter, Depends, HTTPException, Request
import httpx
from pydantic import BaseModel
from ...config import supabase, FRONTEND_URL
from ...middleware.auth import require_user
from ...utils.error_handler import handle_exceptions
from ...utils.github_utils import get_github_token, validate_github_token

class GitHubCodeExchange(BaseModel):
    code: str
    code_verifier: str | None = None

router = APIRouter(
    prefix="/setting",
    tags=["user-setting"]
)

@router.get("/github/connect")
@handle_exceptions(status_code=400)
async def github_connect(user: dict = Depends(require_user)):
    """Get GitHub OAuth login URL from Supabase for connecting GitHub account"""
    # Check if user already has valid GitHub token with required permissions
    github_token = get_github_token(user['id'])
    required_scopes = {'repo', 'admin:repo_hook', 'read:user', 'user:email'}
    
    if github_token:
        try:
            # Raise an exception if token is invalid or missing required scopes
            validate_github_token(github_token, required_scopes)
            raise HTTPException(
                status_code=400,
                detail="GitHub account is already connected with required permissions"
            )
        except HTTPException as e:
            # If the error is not 400, it means token validation failed
            # In that case, continue to get a new token
            if e.status_code == 400:
                raise e

    # Get new GitHub OAuth URL
    auth_url = supabase.auth.sign_in_with_oauth({
        "provider": "github",
        "options": {
            "redirect_to": f"{FRONTEND_URL}/setting/github/callback",
            "skip_http_redirect": True,
            "scopes": "user:email read:user openid repo admin:repo_hook"
        }
    })

    code_verifier = supabase.auth._storage.get_item(
        f"{supabase.auth._storage_key}-code-verifier"
    )

    return {
        "url": auth_url.url,
        "code_verifier": code_verifier
    }

@router.post("/github/verify")
@handle_exceptions(status_code=400)
async def github_verify(body: GitHubCodeExchange, user: dict = Depends(require_user)):
    """Exchange GitHub OAuth code and store access token in the database"""
    # Exchange code for session
    auth_response = supabase.auth.exchange_code_for_session({
        "auth_code": body.code,
        "code_verifier": body.code_verifier,
    })
    
    # Get provider token (GitHub access token)
    session = auth_response.session
    

    # make this user sign out
    supabase.auth.refresh_session(session.refresh_token)
    supabase.auth.sign_out({
        "scope": "local"
    })

    # Store GitHub access token
    supabase.table('users').update({
        'github_access_token': session.provider_token
    }).eq('id', user['id']).execute()
    
    return {
        "message": "GitHub access token successfully stored"
    } 