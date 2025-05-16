from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4
from enum import Enum

class AiGenerationStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

class BRD(BaseModel):
    id: Optional[UUID4] = None
    project_id: Optional[UUID4] = None
    brd_markdown: Optional[str] = None
    status: Optional[AiGenerationStatus] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 