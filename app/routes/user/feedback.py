from fastapi import APIRouter, HTTPException, Depends, status
from ...config import supabase
from ...middleware.auth import require_user
from ...utils.error_handler import handle_exceptions
from ...models import FeedbackCreate

router = APIRouter(
    tags=["user-feedback"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
@handle_exceptions(status_code=500)
async def create_feedback(feedback_data: FeedbackCreate, user: dict = Depends(require_user)):
    """
    Submit new feedback
    """
    try:
        # Insert into database
        result = supabase.table('feedback').insert({
            "user_id": user['id'],
            "title": feedback_data.title,
            "content": feedback_data.content,
            "rating": feedback_data.rating
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create feedback")
        
        return {"message": "Feedback submitted successfully", "id": result.data[0]['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}") 