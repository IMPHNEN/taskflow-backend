from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, UUID4, Field
from decimal import Decimal
from .market_research import MarketResearch
from .mockup import Mockup
from .prd import PRD
from .github_setup import GitHubSetup
from .brd import BRD

class ProjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    objective: str = Field(..., max_length=2000)
    estimated_income: Decimal = Field(..., ge=0)
    estimated_outcome: Decimal = Field(..., ge=0)
    start_date: date
    end_date: date

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = Field(None, max_length=100)
    objective: Optional[str] = None
    estimated_income: Optional[Decimal] = Field(None, ge=0)
    estimated_outcome: Optional[Decimal] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ProjectInDB(ProjectBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Project(ProjectInDB):
    pass

class ProjectDetail(Project):
    brd: Optional[BRD] = None
    prd: Optional[PRD] = None
    market_research: Optional[MarketResearch] = None
    github_setup: Optional[GitHubSetup] = None 
    mockup: Optional[Mockup] = None