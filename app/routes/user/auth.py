from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from ...config import supabase, FRONTEND_URL
from pydantic import BaseModel

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
async def github_login():
    """Get GitHub OAuth login URL from Supabase"""
    try:
        auth_url = supabase.auth.sign_in_with_oauth({
            "provider": "github",
            "options": {
                "redirect_to": f"{FRONTEND_URL}/auth/callback",
                "skip_http_redirect": True  # Return URL instead of redirecting
            }
        })
        code_verifier = supabase.auth._storage.get_item(
            f"{supabase.auth._storage_key}-code-verifier"
        )
        return {
            "url": auth_url.url,
            "code_verifier": code_verifier
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/github/exchange-code")
async def exchange_github_code(body: GitHubCodeExchange):
    """Exchange GitHub OAuth code for session"""
    try:
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
        supabase.table('users').update({
            'github_access_token': session.provider_token
        }).eq('id', user.user.id).execute()
        
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires_in": session.expires_in,
            "user": user.user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh")
async def refresh_token(body: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signout")
async def signout(request: Request):
    """Sign out user and invalidate session"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        token = auth_header.split(' ')[1]
        supabase.auth.sign_out(token)
        return {"message": "Successfully signed out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))