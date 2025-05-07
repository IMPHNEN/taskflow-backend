from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from ...middleware.auth import require_user
from ...models.project import Project, ProjectCreate, ProjectUpdate
from ...config import supabase
from pydantic import BaseModel

# Add new models for market research and mockups
class MarketResearch(BaseModel):
    id: str
    report_markdown: Optional[str]
    created_at: str
    updated_at: str

class Mockup(BaseModel):
    id: str
    preview_url: Optional[str]
    tool_used: Optional[str]
    created_at: str

class ProjectDetail(Project):
    market_research: Optional[MarketResearch] = None
    mockups: Optional[Mockup] = None

router = APIRouter(
    prefix="/project",
    tags=["user-project"]
)

@router.post("")
async def create_project(project: ProjectCreate, user: dict = Depends(require_user)):
    """Create a new project"""
    try:
        project_data = supabase.table('projects').insert({
            **project.model_dump(),
            'user_id': user['id']
        }).execute()
        return {"message": "Project created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[Project])
async def list_projects(user: dict = Depends(require_user)):
    """List all projects for current user"""
    try:
        projects = supabase.table('projects').select('*').eq('user_id', user['id']).execute()
        return projects.data or []  # Return empty list if no projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: str, user: dict = Depends(require_user)):
    """Get a specific project with market research and mockups"""
    try:
        # Get project data
        project = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
        
        if not project or not project.data:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get market research data
        market_research = supabase.table('market_research').select('*').eq('project_id', project_id).maybe_single().execute()
        
        # Get mockups data
        mockups = supabase.table('mockups').select('*').eq('project_id', project_id).maybe_single().execute()

        # Combine the data
        project_detail = project.data
        project_detail['market_research'] = market_research.data if market_research and market_research.data else None
        project_detail['mockups'] = mockups.data if mockups and mockups.data else None

        return project_detail
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{project_id}")
async def update_project(project_id: str, project_update: ProjectUpdate, user: dict = Depends(require_user)):
    """Update a project"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(project_id: str, user: dict = Depends(require_user)):
    """Delete a project"""
    try:
        # Verify project ownership
        project = supabase.table('projects').select('id').eq('id', project_id).eq('user_id', user['id']).maybe_single().execute()
        
        # Handle both None response and empty data cases
        if not project or not project.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Delete project
        supabase.table('projects').delete().eq('id', project_id).execute()
        return {"message": "Project deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/generate-scope")
async def generate_project_scope(project_id: str, user: dict = Depends(require_user)):
    """Generate project scope using AI"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/setup-repository")
async def setup_project_repository(project_id: str, user: dict = Depends(require_user)):
    """Setup GitHub repository for project"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/generate-preview")
async def generate_project_preview(project_id: str, user: dict = Depends(require_user)):
    """Generate project preview/mockup"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/validate-market")
async def validate_market_fit(project_id: str, user: dict = Depends(require_user)):
    """Validate market fit using AI analysis"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 