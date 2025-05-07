from typing import Optional, Callable
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..config import supabase

security = HTTPBearer()

def get_current_user(request: Request) -> dict:
    """Get current user from Supabase session"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        token = auth_header.split(' ')[1]
        user = supabase.auth.get_user(token)
        return user.dict()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def check_user_role(allowed_roles: list[str]) -> Callable:
    """Middleware factory to check user role"""
    async def role_middleware(request: Request):
        try:
            user = get_current_user(request)
            user_data = supabase.table('users').select('role').eq('id', user['user']['id']).single().execute()
            
            if not user_data or user_data.data['role'] not in allowed_roles:
                raise HTTPException(status_code=403, detail="Not enough permissions")
            
            return user['user']
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return role_middleware

# Role-based middleware factories
require_user = check_user_role(['user'])
require_admin = check_user_role(['admin'])
require_super = check_user_role(['super']) 