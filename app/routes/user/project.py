from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import httpx
from ...middleware.auth import require_user
from ...models.project import Project, ProjectCreate, ProjectUpdate, ProjectDetail
from ...config import supabase
from ...utils.error_handler import handle_exceptions
from ...utils.github_utils import get_github_token, validate_github_token
from ...utils.background_tasks import (
    generate_brd_background,
    generate_prd_background,
    generate_tasks_background,
    validate_market_background,
    setup_github_repository_background,
    generate_preview_background
)

router = APIRouter(
    prefix="/project",
    tags=["user-project"]
)

@router.post("")
@handle_exceptions(status_code=400)
async def create_project(project: ProjectCreate, user: dict = Depends(require_user)):
    """Create a new project"""
    # Convert project model to dict
    project_dict = project.model_dump()
    
    # Convert Decimal values to float for JSON serialization
    if 'estimated_income' in project_dict:
        project_dict['estimated_income'] = float(project_dict['estimated_income'])
    if 'estimated_outcome' in project_dict:
        project_dict['estimated_outcome'] = float(project_dict['estimated_outcome'])
    
    # Convert date objects to ISO format strings
    if 'start_date' in project_dict and project_dict['start_date']:
        project_dict['start_date'] = project_dict['start_date'].isoformat()
    if 'end_date' in project_dict and project_dict['end_date']:
        project_dict['end_date'] = project_dict['end_date'].isoformat()
    
    # Insert project with converted values
    project_data = supabase.table('projects').insert({
        **project_dict,
        'user_id': user['id']
    }).execute()
    
    return {"message": "Project created successfully"}

@router.get("", response_model=list[Project])
@handle_exceptions(status_code=500)
async def list_projects(user: dict = Depends(require_user)):
    """List all projects for current user"""
    projects = supabase.table('projects').select('*').eq('user_id', user['id']).execute()
    return projects.data or []  # Return empty list if no projects

@router.get("/{project_id}", response_model=ProjectDetail)
@handle_exceptions(status_code=500)
async def get_project(project_id: str, user: dict = Depends(require_user)):
    """Get a specific project with BRD, market research, mockup, PRD, and GitHub setup"""
    # Get project data
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get related data
    related_tables = ['brd', 'market_research', 'mockup', 'prd', 'github_setup']
    project_detail = project.data

    for table in related_tables:
        result = supabase.table(table).select('*').eq('project_id', project_id).maybe_single().execute()
        project_detail[table] = result.data if result and result.data else None

    return project_detail

@router.patch("/{project_id}")
@handle_exceptions(status_code=500)
async def update_project(project_id: str, project_update: ProjectUpdate, user: dict = Depends(require_user)):
    """Update a project"""
    # Verify project ownership
    project = supabase.table('projects').select('id').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    
    # Handle both None response and empty data cases
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Convert project model to dict with only set values
    update_dict = project_update.model_dump(exclude_unset=True)
    
    # Convert Decimal values to float for JSON serialization
    if 'estimated_income' in update_dict:
        update_dict['estimated_income'] = float(update_dict['estimated_income'])
    if 'estimated_outcome' in update_dict:
        update_dict['estimated_outcome'] = float(update_dict['estimated_outcome'])
    
    # Convert date objects to ISO format strings
    if 'start_date' in update_dict and update_dict['start_date']:
        update_dict['start_date'] = update_dict['start_date'].isoformat()
    if 'end_date' in update_dict and update_dict['end_date']:
        update_dict['end_date'] = update_dict['end_date'].isoformat()
    
    # Update project with converted values
    supabase.table('projects').update(update_dict).eq('id', project_id).execute()
    
    return {"message": "Project updated successfully"}

@router.delete("/{project_id}")
@handle_exceptions(status_code=500)
async def delete_project(project_id: str, user: dict = Depends(require_user)):
    """Delete a project"""
    # Verify project ownership
    project = supabase.table('projects').select('id').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    
    # Handle both None response and empty data cases
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete project
    supabase.table('projects').delete().eq('id', project_id).execute()
    return {"message": "Project deleted successfully"}

@router.post("/{project_id}/generate-brd")
@handle_exceptions(status_code=500)
async def generate_brd(project_id: str, background_tasks: BackgroundTasks, user: dict = Depends(require_user)):
    """Generate BRD (Business Requirements Document) for project"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if BRD record exists
    brd_record = supabase.table('brd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    # If BRD already exists and is not failed, return the existing content
    if brd_record and brd_record.data['status'] != 'failed':
        return {
            "message": f"BRD exists with status: {brd_record.data['status']}",
            "content": brd_record.data.get('brd_markdown', None),
            "status": brd_record.data['status']
        }
    
    # Create new record or update failed record to in_progress
    if not brd_record:
        # Create a new BRD record with status 'in_progress'
        supabase.table('brd').insert({
            'project_id': project_id,
            'status': 'in_progress'
        }).execute()
    else:
        # Update the status to 'in_progress'
        supabase.table('brd').update({'status': 'in_progress'}).eq('project_id', project_id).execute()
    
    # Add the background task
    background_tasks.add_task(generate_brd_background, project_id, project.data)
    
    # Return immediately with in_progress status
    return {
        "message": "BRD generation started",
        "content": None,
        "status": "in_progress"
    }

@router.post("/{project_id}/generate-prd")
@handle_exceptions(status_code=500)
async def generate_prd(project_id: str, background_tasks: BackgroundTasks, user: dict = Depends(require_user)):
    """Generate PRD (Product Requirements Document) for project"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if PRD record exists
    prd_record = supabase.table('prd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    # If PRD already exists and is not failed, return the existing content
    if prd_record and prd_record.data['status'] != 'failed':
        return {
            "message": f"PRD exists with status: {prd_record.data['status']}",
            "content": prd_record.data.get('prd_markdown', None),
            "status": prd_record.data['status']
        }
    
    # Check BRD status - PRD can only be generated if BRD is completed
    brd_record = supabase.table('brd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    if not brd_record or brd_record.data['status'] != 'completed':
        raise HTTPException(status_code=400, detail="BRD must be completed before generating PRD")
    
    # Create new record or update failed record to in_progress
    if not prd_record:
        # Create a new PRD record with status 'in_progress'
        supabase.table('prd').insert({
            'project_id': project_id,
            'status': 'in_progress'
        }).execute()
    else:
        # Update the status to 'in_progress'
        supabase.table('prd').update({'status': 'in_progress'}).eq('project_id', project_id).execute()
    
    # Add the background task
    background_tasks.add_task(
        generate_prd_background, 
        project_id, 
        brd_record.data['brd_markdown'], 
        project.data['name']
    )
    
    # Return immediately with in_progress status
    return {
        "message": "PRD generation started",
        "content": None,
        "status": "in_progress"
    }

@router.post("/{project_id}/generate-scope")
@handle_exceptions(status_code=500)
async def generate_project_scope(project_id: str, background_tasks: BackgroundTasks, user: dict = Depends(require_user)):
    """Generate project scope (tasks) using AI"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check task generation status
    task_status = project.data.get('tasks_generation_status', 'not_started')
    
    # If already in progress or completed, return status
    if task_status != 'failed' and task_status != 'not_started':
        # If completed, return the tasks_generated
        if task_status == 'completed' and project.data.get('tasks_generated'):
            raw_tasks = project.data.get('tasks_generated')
            task_count = len(raw_tasks) if raw_tasks else 0
            
            return {
                "message": "Tasks already generated for this project",
                "task_count": task_count,
                "tasks_generated": raw_tasks,
                "status": "completed"
            }
        
        # If in progress, return status without tasks
        return {
            "message": f"Task generation is {task_status}",
            "task_count": 0,
            "tasks_generated": [],
            "status": task_status
        }
    
    # Check PRD status - Tasks can only be generated if PRD is completed
    prd_record = supabase.table('prd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    if not prd_record.data or prd_record.data['status'] != 'completed':
        raise HTTPException(status_code=400, detail="PRD must be completed before generating tasks")
    
    # Set task generation status to in_progress in the projects table
    supabase.table('projects').update({
        'tasks_generation_status': 'in_progress'
    }).eq('id', project_id).execute()
    
    # Add the background task
    background_tasks.add_task(
        generate_tasks_background, 
        project_id, 
        prd_record.data['prd_markdown']
    )
    
    # Return immediately with in_progress status
    return {
        "message": "Task generation started",
        "task_count": 0,
        "tasks_generated": [],
        "status": "in_progress"
    }

@router.post("/{project_id}/validate-market")
@handle_exceptions(status_code=500)
async def validate_market_fit(project_id: str, background_tasks: BackgroundTasks, user: dict = Depends(require_user)):
    """Validate market fit using AI analysis"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if market research record exists
    market_record = supabase.table('market_research').select('*').eq('project_id', project_id).maybe_single().execute()
    
    # If market research already exists and is not failed, return the existing content
    if market_record and market_record.data['status'] != 'failed':
        return {
            "message": f"Market validation exists with status: {market_record.data['status']}",
            "content": market_record.data.get('report_markdown', None),
            "status": market_record.data['status']
        }
    
    # Create new record or update failed record to in_progress
    if not market_record:
        # Create a new market research record with status 'in_progress'
        supabase.table('market_research').insert({
            'project_id': project_id,
            'status': 'in_progress'
        }).execute()
    else:
        # Update the status to 'in_progress'
        supabase.table('market_research').update({'status': 'in_progress'}).eq('project_id', project_id).execute()
    
    # Add the background task
    background_tasks.add_task(
        validate_market_background, 
        project_id, 
        project.data['objective']
    )
    
    # Return immediately with in_progress status
    return {
        "message": "Market validation started",
        "content": None,
        "status": "in_progress"
    }

@router.post("/{project_id}/setup-repository")
@handle_exceptions(status_code=500)
async def setup_project_repository(project_id: str, background_tasks: BackgroundTasks, user: dict = Depends(require_user)):
    """Setup GitHub repository for project"""
    # Get github access token from user
    github_access_token = get_github_token(user['id'])
    
    if not github_access_token:
        raise HTTPException(status_code=400, detail="You need to connect your GitHub account to use this feature")
    
    # Validate token and check required scopes
    required_scopes = {'repo', 'admin:repo_hook', 'read:user', 'user:email'}
    user_infos = validate_github_token(github_access_token, required_scopes)
    
    # Get github username
    github_username = user_infos.get('login')

    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if GitHub setup record exists
    github_record = supabase.table('github_setup').select('*').eq('project_id', project_id).maybe_single().execute()
    
    # If setup already exists and is not failed, return the existing content
    if github_record and github_record.data['status'] != 'failed':
        return {
            "message": f"GitHub setup exists with status: {github_record.data['status']}",
            "repository_url": github_record.data.get('repository_url', None),
            "status": github_record.data['status']
        }
    
    # Check PRD and tasks status - Repository can only be set up if PRD is completed and tasks are generated
    prd_record = supabase.table('prd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    if not prd_record or prd_record.data['status'] != 'completed':
        raise HTTPException(status_code=400, detail="PRD must be completed before setting up repository")
        
    if project.data.get('tasks_generation_status') != 'completed':
        raise HTTPException(status_code=400, detail="Tasks must be generated before setting up repository")
    
    # Create new record or update failed record to in_progress
    if not github_record:
        # Create a new GitHub setup record with status 'in_progress'
        supabase.table('github_setup').insert({
            'project_id': project_id,
            'status': 'in_progress'
        }).execute()
    else:
        # Update the status to 'in_progress'
        supabase.table('github_setup').update({'status': 'in_progress'}).eq('project_id', project_id).execute()
    
    # Add the background task
    background_tasks.add_task(
        setup_github_repository_background,
        project_id,
        github_access_token
    )
    
    # Return immediately with in_progress status
    return {
        "message": "GitHub repository setup started",
        "repository_url": None,
        "status": "in_progress"
    }

@router.post("/{project_id}/generate-preview")
@handle_exceptions(status_code=500)
async def generate_project_preview(project_id: str, background_tasks: BackgroundTasks, user: dict = Depends(require_user)):
    """Generate project preview/mockup using Lovable"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if mockup record exists
    mockup_record = supabase.table('mockup').select('*').eq('project_id', project_id).maybe_single().execute()
    
    # If mockup already exists and is not failed, return the existing content
    if mockup_record and mockup_record.data['status'] != 'failed':
        return {
            "message": f"Preview exists with status: {mockup_record.data['status']}",
            "preview_url": mockup_record.data.get('preview_url', None),
            "tool_used": mockup_record.data.get('tool_used', None),
            "status": mockup_record.data['status']
        }
    
    # Check BRD status - Preview can only be generated if BRD is completed
    brd_record = supabase.table('brd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    if not brd_record or brd_record.data['status'] != 'completed':
        raise HTTPException(status_code=400, detail="BRD must be completed before generating preview")
    
    # Create new record or update failed record to in_progress
    if not mockup_record:
        # Create a new mockup record with status 'in_progress'
        supabase.table('mockup').insert({
            'project_id': project_id,
            'status': 'in_progress'
        }).execute()
    else:
        # Update the status to 'in_progress'
        supabase.table('mockup').update({'status': 'in_progress'}).eq('project_id', project_id).execute()
    
    # Add the background task
    background_tasks.add_task(generate_preview_background, project_id)
    
    # Return immediately with in_progress status
    return {
        "message": "Preview generation started",
        "preview_url": None,
        "tool_used": None,
        "status": "in_progress"
    } 