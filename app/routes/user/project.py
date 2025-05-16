from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from ...middleware.auth import require_user
from ...models.project import Project, ProjectCreate, ProjectUpdate, ProjectDetail
from ...config import supabase
from ...utils.error_handler import handle_exceptions

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
    """Get a specific project with market research, mockup, PRD, and GitHub setup"""
    # Get project data
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    
    if not project or not project.data:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get related data
    related_tables = ['market_research', 'mockup', 'prd', 'github_setup']
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

@router.post("/{project_id}/generate-scope")
@handle_exceptions(status_code=500)
async def generate_project_scope(project_id: str, user: dict = Depends(require_user)):
    """Generate project scope using AI"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # TODO: Implement AI logic using Agno
    return {
        "message": "Project scope generated",
        "scope":[
            {
                "title": "Create a landing page",
                "description": "Create a landing page for the project",
                "task_type": "epic",
                "position": 1,
            },
            {
                "title": "Build a login form",
                "description": "Build a login form for the project",
                "task_type": "feature",
                "position": 2,
            }
        ]
    }

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

@router.post("/{project_id}/validate-market")
@handle_exceptions(status_code=500)
async def validate_market_fit(project_id: str, user: dict = Depends(require_user)):
    """Validate market fit using AI analysis"""
    # Verify project ownership
    project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # TODO: Implement market validation using Firecrawl and Agno
    return {
        "message": "Market validation completed",
        "analysis": {
            "markdown": "## Market Analysis\n\nBased on the analysis, the market is a good fit for the project."
        }
    } 