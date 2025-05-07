from fastapi import APIRouter, HTTPException, Request
from ...config import supabase
from ...models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["admin-auth"]
)

@router.post("/login")
async def admin_login(username: str, password: str):
    """Admin login with username and password"""
    try:
        # Sign in with email/password
        auth_response = supabase.auth.sign_in_with_password({
            "email": username,
            "password": password
        })
        
        # Verify admin role
        user = supabase.auth.get_user(auth_response.session.access_token)
        user_data = supabase.table('users').select('role').eq('id', user.user.id).single().execute()
        if not user_data.data or user_data.data['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Not authorized as admin")
        
        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "expires_in": auth_response.session.expires_in,
            "user": user.user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        response = supabase.auth.refresh_session(refresh_token)
        # Verify admin role
        user = supabase.auth.get_user(response.session.access_token)
        user_data = supabase.table('users').select('role').eq('id', user.user.id).single().execute()
        if not user_data.data or user_data.data['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Not authorized as admin")
            
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signout")
async def signout(request: Request):
    """Sign out admin and invalidate session"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        token = auth_header.split(' ')[1]
        supabase.auth.sign_out(token)
        return {"message": "Successfully signed out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 