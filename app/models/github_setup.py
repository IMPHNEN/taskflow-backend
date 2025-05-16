from pydantic import BaseModel
from typing import Optional

class GitHubSetup(BaseModel):
    id: str
    repository_url: Optional[str]
    status: str  # ai_generation_status enum
    created_at: str
    updated_at: str 