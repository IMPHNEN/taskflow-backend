"""
Background task functions for AI generation services.
"""
from ..config import supabase, brd_service, prd_service, task_service, market_validation_service, github_setup_service, preview_service
from .ai_utils import llm_to_tasks

async def generate_brd_background(project_id: str, project_data: dict):
    """Background task to generate BRD"""
    try:
        brd_result = await brd_service.generate_brd({
            'project_name': project_data['name'],
            'project_description': project_data['objective'],
            'start_date': project_data['start_date'],
            'end_date': project_data['end_date'],
        }, project_id)
        
        if brd_result['status'] == 'success':
            # Update the BRD record with the content and 'completed' status
            supabase.table('brd').update({
                'brd_markdown': brd_result['content'],
                'status': 'completed'
            }).eq('project_id', project_id).execute()
        else:
            # Update the status to 'failed'
            supabase.table('brd').update({'status': 'failed'}).eq('project_id', project_id).execute()
    except Exception as e:
        # Update the status to 'failed'
        supabase.table('brd').update({'status': 'failed'}).eq('project_id', project_id).execute()

async def generate_prd_background(project_id: str, brd_content: str, project_name: str):
    """Background task to generate PRD"""
    try:
        prd_result = await prd_service.generate_prd(
            brd_content,
            project_name,
            project_id
        )
        
        if prd_result['status'] == 'success':
            # Update the PRD record with the content and 'completed' status
            supabase.table('prd').update({
                'prd_markdown': prd_result['content'],
                'status': 'completed'
            }).eq('project_id', project_id).execute()
        else:
            # Update the status to 'failed'
            supabase.table('prd').update({'status': 'failed'}).eq('project_id', project_id).execute()
    except Exception as e:
        # Update the status to 'failed'
        supabase.table('prd').update({'status': 'failed'}).eq('project_id', project_id).execute()

async def generate_tasks_background(project_id: str, prd_content: str):
    """Background task to generate tasks"""
    try:
        # Update project status to in_progress
        supabase.table('projects').update({
            'tasks_generation_status': 'in_progress'
        }).eq('id', project_id).execute()
        
        task_result = await task_service.generate_tasks(prd_content, project_id)
        
        if 'items' in task_result:
            # Convert LLM generated tasks to task records
            task_records = llm_to_tasks(task_result['items'], project_id)
            
            # Insert tasks into the database
            supabase.table('tasks').insert(task_records).execute()
            
            # Update project status to completed and store raw tasks
            supabase.table('projects').update({
                'tasks_generation_status': 'completed',
                'tasks_generated': task_records
            }).eq('id', project_id).execute()
        else:
            # Update project status to failed
            supabase.table('projects').update({
                'tasks_generation_status': 'failed'
            }).eq('id', project_id).execute()
    except Exception as e:
        # Update project status to failed
        supabase.table('projects').update({
            'tasks_generation_status': 'failed'
        }).eq('id', project_id).execute()

async def validate_market_background(project_id: str, project_objective: str):
    """Background task to validate market"""
    try:
        market_result = await market_validation_service.run_market_validation(project_objective, project_id)
        
        if market_result['status'] == 'success':
            # Update the market research record with the content and 'completed' status
            supabase.table('market_research').update({
                'report_markdown': market_result['content'],
                'status': 'completed'
            }).eq('project_id', project_id).execute()
        else:
            # Update the status to 'failed'
            supabase.table('market_research').update({'status': 'failed'}).eq('project_id', project_id).execute()
    except Exception as e:
        # Update the status to 'failed'
        supabase.table('market_research').update({'status': 'failed'}).eq('project_id', project_id).execute()

async def setup_github_repository_background(project_id: str, github_token: str):
    """Background task to set up GitHub repository"""
    try:
        # Get project details and PRD content
        project = supabase.table('projects').select('*').eq('id', project_id).single().execute()
        prd = supabase.table('prd').select('*').eq('project_id', project_id).single().execute()
        
        if not project.data or not prd.data or prd.data['status'] != 'completed':
            raise ValueError("Project or PRD not found or PRD not completed")
        
        # Update github_setup status to in_progress
        supabase.table('github_setup').update({
            'status': 'in_progress'
        }).eq('project_id', project_id).execute()
        
        # Run repository setup
        result = await github_setup_service.setup_repository(
            project_details=project.data,
            prd_content=prd.data['prd_markdown'],
            github_token=github_token,
            project_id=project_id
        )
        
        if result['status'] == 'success':
            # Update github_setup record with results
            supabase.table('github_setup').update({
                'repository_url': result['repository_url'],
                'status': 'completed'
            }).eq('project_id', project_id).execute()
        else:
            # Update status to failed
            supabase.table('github_setup').update({
                'status': 'failed'
            }).eq('project_id', project_id).execute()
            
    except Exception as e:
        # Update status to failed
        supabase.table('github_setup').update({
            'status': 'failed'
        }).eq('project_id', project_id).execute()

async def generate_preview_background(project_id: str):
    """Background task to generate preview/mockup"""
    try:
        # Get project details and BRD content
        project = supabase.table('projects').select('*').eq('id', project_id).single().execute()
        brd = supabase.table('brd').select('*').eq('project_id', project_id).single().execute()
        
        if not project.data or not brd.data or brd.data['status'] != 'completed':
            raise ValueError("Project or BRD not found or BRD not completed")
        
        # Run preview generation
        result = await preview_service.generate_preview(
            project_details=project.data,
            brd_content=brd.data['brd_markdown'],
            user_id=project_id
        )
        
        if result['status'] == 'success':
            # Update mockup record with results
            supabase.table('mockup').update({
                'preview_url': result['preview_url'],
                'tool_used': 'Lovable',
                'status': 'completed'
            }).eq('project_id', project_id).execute()
        else:
            # Update status to failed
            supabase.table('mockup').update({
                'status': 'failed'
            }).eq('project_id', project_id).execute()
            
    except Exception as e:
        # Update status to failed
        supabase.table('mockup').update({
            'status': 'failed'
        }).eq('project_id', project_id).execute() 