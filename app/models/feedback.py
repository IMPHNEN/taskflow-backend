from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4, Field, validator

class FeedbackBase(BaseModel):
    title: str
    content: str
    rating: int
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackInDB(FeedbackBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Feedback(FeedbackInDB):
    pass 