from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from ...config import supabase, FRONTEND_URL
from pydantic import BaseModel
from ...utils.error_handler import handle_exceptions

class GitHubCodeExchange(BaseModel):
    code: str
    code_verifier: str | None = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

router = APIRouter(
    prefix="/auth",
    tags=["user-auth"]
)

@router.get("/github/login")
@handle_exceptions(status_code=400)
async def github_login():
    """Get GitHub OAuth login URL from Supabase"""
    auth_url = supabase.auth.sign_in_with_oauth({
        "provider": "github",
        "options": {
            "redirect_to": f"{FRONTEND_URL}/auth/callback/github",
            "skip_http_redirect": True,  # Return URL instead of redirecting
            "scopes": "user:email read:user openid"
        }
    })
    code_verifier = supabase.auth._storage.get_item(
        f"{supabase.auth._storage_key}-code-verifier"
    )
    return {
        "url": auth_url.url,
        "code_verifier": code_verifier
    }

@router.post("/github/exchange-code")
@handle_exceptions(status_code=400)
async def exchange_github_code(body: GitHubCodeExchange):
    """Exchange GitHub OAuth code for session"""
    # Exchange code for session
    auth_response = supabase.auth.exchange_code_for_session({
        "auth_code": body.code,
        "code_verifier": body.code_verifier
    })
    
    # Get user data including provider token (GitHub access token)
    session = auth_response.session
    user = supabase.auth.get_user(session.access_token)
    
    # Verify user role
    user_data = supabase.table('users').select('role').eq('id', user.user.id).maybe_single().execute()
    if not user_data or not user_data.data or user_data.data['role'] != 'user':
        raise HTTPException(status_code=403, detail="Not authorized as user")
    
    # Store GitHub access token
    # supabase.table('users').update({
    #     'github_access_token': session.provider_token
    # }).eq('id', user.user.id).execute()
    
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expires_in": session.expires_in,
        "user": user.user
    }

@router.post("/refresh")
@handle_exceptions(status_code=400)
async def refresh_token(body: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    response = supabase.auth.refresh_session(body.refresh_token)
    # Verify user role
    user = supabase.auth.get_user(response.session.access_token)
    user_data = supabase.table('users').select('role').eq('id', user.user.id).maybe_single().execute()
    if not user_data or not user_data.data or user_data.data['role'] != 'user':
        raise HTTPException(status_code=403, detail="Not authorized as user")
        
    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "expires_in": response.session.expires_in
    }

@router.post("/signout")
@handle_exceptions(status_code=400)
async def signout(body: RefreshTokenRequest):
    """Sign out user and invalidate session"""
    # call refresh token
    supabase.auth.refresh_session(body.refresh_token)
    supabase.auth.sign_out({
        "scope": "local"
    })
    return {"message": "Successfully signed out"}