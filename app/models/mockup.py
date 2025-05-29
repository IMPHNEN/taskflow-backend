from pydantic import BaseModel
from typing import Optional

class Mockup(BaseModel):
    id: str
    preview_url: Optional[str]
    tool_used: Optional[str]
    status: str  # ai_generation_status enum
    created_at: str
    updated_at: str 