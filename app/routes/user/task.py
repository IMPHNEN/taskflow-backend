from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from ...middleware.auth import require_user
from ...models.task import Task, TaskCreate, TaskUpdate, TaskStatus
from ...config import supabase
from postgrest.exceptions import APIError

router = APIRouter(
    prefix="/task",
    tags=["user-task"]
)

@router.post("/{project_id}")
async def create_task(project_id: str, task: TaskCreate, user: dict = Depends(require_user)):
    """Create a new task in a project"""
    try:
        # Verify project ownership
        project = supabase.table('projects').select('id').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
        if not project or not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create task
        supabase.table('tasks').insert({
            **task.model_dump(),
            'project_id': project_id
        }).execute()
        
        return {"message": "Task created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}", response_model=list[Task])
async def list_tasks(
    project_id: str,
    status: Optional[TaskStatus] = None,
    user: dict = Depends(require_user)
):
    """List all tasks in a project"""
    try:
        # Verify project ownership
        project = supabase.table('projects').select('id').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
        if not project or not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Build query
        query = supabase.table('tasks').select('*').eq('project_id', project_id)
        if status:
            query = query.eq('status', status)
        
        # Execute query
        tasks = query.order('position').execute()
        return tasks.data or []  # Return empty list if no tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/{task_id}", response_model=Task)
async def get_task(project_id: str, task_id: str, user: dict = Depends(require_user)):
    """Get a specific task"""
    try:
        # Verify project ownership
        project = supabase.table('projects').select('id').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
        if not project or not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get task
        task = supabase.table('tasks').select('*').eq('id', task_id).eq('project_id', project_id).maybe_single().execute()
        if not task or not task.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{project_id}/{task_id}")
async def update_task(
    project_id: str,
    task_id: str,
    task_update: TaskUpdate,
    user: dict = Depends(require_user)
):
    """Update a task"""
    try:
        # Verify project ownership
        project = supabase.table('projects').select('id').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
        if not project or not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Verify task exists
        task = supabase.table('tasks').select('id').eq('id', task_id).eq('project_id', project_id).maybe_single().execute()
        if not task or not task.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update task
        supabase.table('tasks').update(
            task_update.model_dump(exclude_unset=True)
        ).eq('id', task_id).execute()
        
        return {"message": "Task updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}/{task_id}")
async def delete_task(project_id: str, task_id: str, user: dict = Depends(require_user)):
    """Delete a task"""
    try:
        # Verify project ownership
        project = supabase.table('projects').select('id').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
        if not project or not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Verify task exists
        task = supabase.table('tasks').select('id').eq('id', task_id).eq('project_id', project_id).maybe_single().execute()
        if not task or not task.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Delete task
        supabase.table('tasks').delete().eq('id', task_id).execute()
        return {"message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{project_id}/reorder")
async def reorder_tasks(
    project_id: str,
    task_orders: list[dict],
    user: dict = Depends(require_user)
):
    """Reorder tasks in a project"""
    try:
        # Verify project ownership
        project = supabase.table('projects').select('id').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
        if not project or not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update task positions
        for order in task_orders:
            supabase.table('tasks').update({
                'position': order['position']
            }).eq('id', order['task_id']).execute()
        
        return {"message": "Tasks reordered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 