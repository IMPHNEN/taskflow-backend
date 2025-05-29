from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4

class UserBase(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider_id: Optional[str] = None
    github_access_token: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    is_banned: Optional[bool] = None

class UserInDB(UserBase):
    id: UUID4
    role: str = 'user'
    is_banned: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserInDB):
    pass 