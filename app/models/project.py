from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, UUID4, Field
from decimal import Decimal

class ProjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    objective: str
    estimated_income: Optional[Decimal] = None
    estimated_outcome: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    github_url: Optional[str] = Field(None, max_length=255)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = Field(None, max_length=100)
    objective: Optional[str] = None

class ProjectInDB(ProjectBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Project(ProjectInDB):
    pass 