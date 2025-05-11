from fastapi import APIRouter, HTTPException, Depends
from ...config import supabase
from pydantic import BaseModel
from ...middleware.auth import require_user
from ...utils.error_handler import handle_exceptions

router = APIRouter(
    tags=["user-info"]
)

class UserInfo(BaseModel):
    id: str
    full_name: str | None = None
    avatar_url: str | None = None

@router.get("/me", response_model=UserInfo)
@handle_exceptions(status_code=500)
async def get_current_user(user: dict = Depends(require_user)):
    """Get current user's basic information"""
    # Get user data from database
    user_data = supabase.table('users').select('id,full_name,avatar_url').eq('id', user['id']).maybe_single().execute()
    if not user_data or not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_data.data 