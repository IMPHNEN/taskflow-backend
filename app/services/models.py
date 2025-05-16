"""
Pydantic models for AI service data.
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict


class TaskType(str, Enum):
    EPIC = "epic"
    FEATURE = "feature"
    TASK = "task"


class BaseTaskItem(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "epic_1",
            "title": "Epic Title",
            "description": "Description of the epic",
            "task_type": "epic",
            "position": 1,
            "parent_id": None
        }
    })

    id: str
    title: str
    description: str
    task_type: TaskType
    position: int
    parent_id: Optional[str] = None


class Epic(BaseTaskItem):
    @model_validator(mode="after")
    def must_be_epic(self):
        if self.task_type != TaskType.EPIC:
            raise ValueError('task_type must be "epic"')
        return self


class Feature(BaseTaskItem):
    @model_validator(mode="after")
    def must_be_feature(self):
        if self.task_type != TaskType.FEATURE:
            raise ValueError('task_type must be "feature"')
        return self


class Task(BaseTaskItem):
    estimated_hours: int

    @model_validator(mode="after")
    def must_be_task(self):
        if self.task_type != TaskType.TASK:
            raise ValueError('task_type must be "task"')
        return self

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "task_1",
            "title": "Task Title",
            "description": "Short one or two sentence summary of the task.",
            "task_type": "task",
            "position": 1,
            "parent_id": "feature_1",
            "estimated_hours": 8,
        }
    })


class TaskHierarchy(BaseModel):
    items: List[BaseTaskItem]

    @model_validator(mode="after")
    def validate_hierarchy(self):
        items = self.items

        # Collect all IDs by type
        epic_ids = {item.id for item in items if item.task_type == TaskType.EPIC}
        feature_items = [item for item in items if item.task_type == TaskType.FEATURE]
        task_items = [item for item in items if item.task_type == TaskType.TASK]
        feature_ids = {item.id for item in feature_items}

        # Validate parents
        for feature in feature_items:
            if feature.parent_id not in epic_ids:
                raise ValueError(f"Feature {feature.id} has invalid parent_id: {feature.parent_id}")

        for task in task_items:
            if task.parent_id not in feature_ids:
                raise ValueError(f"Task {task.id} has invalid parent_id: {task.parent_id}")

        return self


class ProjectRequest(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description or PRD content")


class MarketValidationRequest(BaseModel):
    project_description: str = Field(..., description="Project description for market validation") 