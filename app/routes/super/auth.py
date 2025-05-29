from fastapi import APIRouter, HTTPException, Request
from ...config import supabase
from ...models.user import User
from ...utils.error_handler import handle_exceptions

router = APIRouter(
    prefix="/auth",
    tags=["super-auth"]
)

@router.post("/login")
@handle_exceptions(status_code=400)
async def super_login(username: str, password: str):
    """Super admin login with username and password"""
    # Sign in with email/password
    auth_response = supabase.auth.sign_in_with_password({
        "email": username,
        "password": password
    })
    
    # Verify super admin role
    user = supabase.auth.get_user(auth_response.session.access_token)
    user_data = supabase.table('users').select('role').eq('id', user.user.id).single().execute()
    if not user_data.data or user_data.data['role'] != 'super':
        raise HTTPException(status_code=403, detail="Not authorized as super admin")
    
    return {
        "access_token": auth_response.session.access_token,
        "refresh_token": auth_response.session.refresh_token,
        "expires_in": auth_response.session.expires_in,
        "user": user.user
    }

@router.post("/refresh")
@handle_exceptions(status_code=400)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    response = supabase.auth.refresh_session(refresh_token)
    # Verify super admin role
    user = supabase.auth.get_user(response.session.access_token)
    user_data = supabase.table('users').select('role').eq('id', user.user.id).single().execute()
    if not user_data.data or user_data.data['role'] != 'super':
        raise HTTPException(status_code=403, detail="Not authorized as super admin")
        
    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "expires_in": response.session.expires_in
    }

@router.post("/signout")
@handle_exceptions(status_code=400)
async def signout(request: Request):
    """Sign out super admin and invalidate session"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    token = auth_header.split(' ')[1]
    supabase.auth.sign_out(token)
    return {"message": "Successfully signed out"}