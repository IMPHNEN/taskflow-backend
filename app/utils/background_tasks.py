"""
Background task functions for AI generation services.
"""
from ..config import supabase, brd_service, prd_service, task_service, market_validation_service
from .ai_utils import llm_to_tasks

async def generate_brd_background(project_id: str, project_data: dict):
    """Background task to generate BRD"""
    try:
        brd_result = await brd_service.generate_brd({
            'project_name': project_data['name'],
            'project_description': project_data['objective'],
            'start_date': project_data['start_date'],
            'end_date': project_data['end_date'],
        })
        
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
            brd_content=brd_content,
            project_name=project_name
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
        
        task_result = await task_service.generate_tasks(prd_content)
        
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
        market_result = await market_validation_service.run_market_validation(project_objective)
        
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