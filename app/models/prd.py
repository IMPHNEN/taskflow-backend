from pydantic import BaseModel
from typing import Optional

class PRD(BaseModel):
    id: str
    prd_markdown: Optional[str]
    status: str  # ai_generation_status enum
    created_at: str
    updated_at: str 