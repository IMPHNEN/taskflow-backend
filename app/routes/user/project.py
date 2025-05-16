from fastapi import APIRouter, Depends, HTTPException
from ...middleware.auth import require_user
from ...models.project import Project, ProjectCreate, ProjectUpdate, ProjectDetail
from ...config import supabase, brd_service, prd_service, task_service, market_validation_service
from ...utils.error_handler import handle_exceptions
from ...utils.ai_utils import llm_to_tasks

router = APIRouter(
    prefix="/project",
    tags=["user-project"]
)

@router.post("")
@handle_exceptions(status_code=400)
async def create_project(project: ProjectCreate, user: dict = Depends(require_user)):
    """Create a new project"""
    project_data = supabase.table('projects').insert({
        **project.model_dump(),
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
    
    # Update project
    supabase.table('projects').update(
        project_update.model_dump(exclude_unset=True)
    ).eq('id', project_id).execute()
    
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
async def generate_brd(project_id: str, user: dict = Depends(require_user)):
    """Generate BRD (Business Requirements Document) for project"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if BRD record exists, if not create it
    brd_record = supabase.table('brd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    if not brd_record.data:
        # Create a new BRD record with status 'in_progress'
        supabase.table('brd').insert({
            'project_id': project_id,
            'status': 'in_progress'
        }).execute()
    else:
        # Update the status to 'in_progress'
        supabase.table('brd').update({'status': 'in_progress'}).eq('project_id', project_id).execute()
    
    try:
        # Use the BRD service instance from config
        brd_result = await brd_service.generate_brd({
            'project_name': project.data['name'],
            'project_description': project.data['objective'],
            'start_date': project.data['start_date'],
            'end_date': project.data['end_date'],
        })
        
        if brd_result['status'] == 'success':
            # Update the BRD record with the content and 'completed' status
            supabase.table('brd').update({
                'brd_markdown': brd_result['content'],
                'status': 'completed'
            }).eq('project_id', project_id).execute()
            
            return {
                "message": "BRD generated successfully",
                "content": brd_result['content']
            }
        else:
            # Update the status to 'failed'
            supabase.table('brd').update({'status': 'failed'}).eq('project_id', project_id).execute()
            raise HTTPException(status_code=500, detail=f"BRD generation failed: {brd_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        # Update the status to 'failed'
        supabase.table('brd').update({'status': 'failed'}).eq('project_id', project_id).execute()
        raise HTTPException(status_code=500, detail=f"BRD generation failed: {str(e)}")

@router.post("/{project_id}/generate-prd")
@handle_exceptions(status_code=500)
async def generate_prd(project_id: str, user: dict = Depends(require_user)):
    """Generate PRD (Product Requirements Document) for project"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check BRD status - PRD can only be generated if BRD is completed
    brd_record = supabase.table('brd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    if not brd_record.data or brd_record.data['status'] != 'completed':
        raise HTTPException(status_code=400, detail="BRD must be completed before generating PRD")
    
    # Check if PRD record exists, if not create it
    prd_record = supabase.table('prd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    if not prd_record.data:
        # Create a new PRD record with status 'in_progress'
        supabase.table('prd').insert({
            'project_id': project_id,
            'status': 'in_progress'
        }).execute()
    else:
        # Update the status to 'in_progress'
        supabase.table('prd').update({'status': 'in_progress'}).eq('project_id', project_id).execute()
    
    try:
        # Use the PRD service instance from config
        prd_result = await prd_service.generate_prd(
            brd_content=brd_record.data['brd_markdown'], 
            project_name=project.data['name']
        )
        
        if prd_result['status'] == 'success':
            # Update the PRD record with the content and 'completed' status
            supabase.table('prd').update({
                'prd_markdown': prd_result['content'],
                'status': 'completed'
            }).eq('project_id', project_id).execute()
            
            return {
                "message": "PRD generated successfully",
                "content": prd_result['content']
            }
        else:
            # Update the status to 'failed'
            supabase.table('prd').update({'status': 'failed'}).eq('project_id', project_id).execute()
            raise HTTPException(status_code=500, detail=f"PRD generation failed: {prd_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        # Update the status to 'failed'
        supabase.table('prd').update({'status': 'failed'}).eq('project_id', project_id).execute()
        raise HTTPException(status_code=500, detail=f"PRD generation failed: {str(e)}")

@router.post("/{project_id}/generate-scope")
@handle_exceptions(status_code=500)
async def generate_project_scope(project_id: str, user: dict = Depends(require_user)):
    """Generate project scope (tasks) using AI"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check PRD status - Tasks can only be generated if PRD is completed
    prd_record = supabase.table('prd').select('*').eq('project_id', project_id).maybe_single().execute()
    
    if not prd_record.data or prd_record.data['status'] != 'completed':
        raise HTTPException(status_code=400, detail="PRD must be completed before generating tasks")
    
    try:
        # Use the task service instance from config
        task_result = await task_service.generate_tasks(prd_record.data['prd_markdown'])
        
        if 'items' in task_result:
            # Convert LLM generated tasks to task records
            task_records = llm_to_tasks(task_result['items'], project_id)
            
            # Insert tasks into the database
            supabase.table('tasks').insert(task_records).execute()
            
            return {
                "message": "Project scope generated successfully",
                "task_count": len(task_records),
                "tasks": task_records
            }
        else:
            raise HTTPException(status_code=500, detail="Task generation failed: Invalid task structure")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task generation failed: {str(e)}")

@router.post("/{project_id}/validate-market")
@handle_exceptions(status_code=500)
async def validate_market_fit(project_id: str, user: dict = Depends(require_user)):
    """Validate market fit using AI analysis"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if market research record exists, if not create it
    market_record = supabase.table('market_research').select('*').eq('project_id', project_id).maybe_single().execute()
    
    if not market_record.data:
        # Create a new market research record with status 'in_progress'
        supabase.table('market_research').insert({
            'project_id': project_id,
            'status': 'in_progress'
        }).execute()
    else:
        # Update the status to 'in_progress'
        supabase.table('market_research').update({'status': 'in_progress'}).eq('project_id', project_id).execute()
    
    try:
        # Use the market validation service instance from config
        market_result = await market_validation_service.run_market_validation(project.data['objective'])
        
        if market_result['status'] == 'success':
            # Update the market research record with the content and 'completed' status
            supabase.table('market_research').update({
                'report_markdown': market_result['content'],
                'status': 'completed'
            }).eq('project_id', project_id).execute()
            
            return {
                "message": "Market validation completed successfully",
                "content": market_result['content']
            }
        else:
            # Update the status to 'failed'
            supabase.table('market_research').update({'status': 'failed'}).eq('project_id', project_id).execute()
            raise HTTPException(status_code=500, detail=f"Market validation failed: {market_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        # Update the status to 'failed'
        supabase.table('market_research').update({'status': 'failed'}).eq('project_id', project_id).execute()
        raise HTTPException(status_code=500, detail=f"Market validation failed: {str(e)}")

@router.post("/{project_id}/setup-repository")
@handle_exceptions(status_code=500)
async def setup_project_repository(project_id: str, user: dict = Depends(require_user)):
    """Setup GitHub repository for project"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # TODO: Implement GitHub repository setup using MCP
    return {
        "message": "Repository setup completed",
        "repository": {
            "name": "example-project",
            "url": "https://github.com/username/example-project",
        }
    }

@router.post("/{project_id}/generate-preview")
@handle_exceptions(status_code=500)
async def generate_project_preview(project_id: str, user: dict = Depends(require_user)):
    """Generate project preview/mockup"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # TODO: Implement preview generation using v0.dev or similar
    return {
        "message": "Preview generated",
        "preview": {
            "url": "https://example.com/preview.png",
            "type": "landing_page"
        }
    } 