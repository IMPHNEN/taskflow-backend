from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4, Field
from enum import Enum

class TaskType(str, Enum):
    epic = "epic"
    feature = "feature"
    task = "task"

class TaskStatus(str, Enum):
    backlog = "backlog"
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class TaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    task_type: TaskType
    status: TaskStatus = TaskStatus.backlog
    # position: int = Field(..., gt=0)
    story_point: int = Field(..., gt=0)
    parent_id: Optional[UUID4] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    task_type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    position: Optional[int] = Field(None, gt=0)
    story_point: Optional[int] = Field(None, ge=0)
    parent_id: Optional[UUID4] = None

class TaskInDB(TaskBase):
    id: UUID4
    project_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Task(TaskInDB):
    pass 