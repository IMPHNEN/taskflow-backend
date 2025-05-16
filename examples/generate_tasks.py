"""
Task Generator Example

This example demonstrates how to use the TaskGeneratorService to generate 
a task hierarchy from a Product Requirements Document (PRD).
"""
import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any

# Add the project root directory to the Python path if running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.task_generator import TaskGeneratorService
from app.utils.ai_utils import save_to_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def generate_tasks(prd_content: str, save_file: bool = True) -> Dict[str, Any]:
    """
    Generate a task hierarchy from PRD content.
    
    Args:
        prd_content: The content of a PRD document
        save_file: Whether to save the tasks to a file
        
    Returns:
        Dictionary with task generation results
    """
    logger.info("Generating task hierarchy from PRD")
    
    # Initialize the service
    task_service = TaskGeneratorService()
    
    try:
        # Generate tasks
        result = await task_service.generate_tasks(prd_content)
        
        logger.info(f"✅ Task generation successful: {len(result.get('items', []))} tasks")
        
        # Save to file if requested
        if save_file:
            # Save using the utility function with timestamp
            saved_path = save_to_file(result, "task_results")
        
        return {
            "status": "success",
            "content": result,
            "file_path": saved_path if save_file else None
        }
        
    except Exception as e:
        logger.error(f"❌ Task generation failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


async def main():
    """Run the example with a sample PRD."""
    project_name = "TaskFlow"
    
    # Try to load PRD from file if it exists
    try:
        with open(f"examples/output_{project_name.lower()}_prd.md", "r", encoding="utf-8") as f:
            prd_content = f.read()
        logger.info("Using PRD from existing file")
    except FileNotFoundError:
        # Use a minimal sample PRD if no file is found
        prd_content = """# PRODUCT REQUIREMENTS DOCUMENT (PRD)

## TaskFlow

### Introduction
TaskFlow is a project management tool for software developers that uses AI to generate tasks from PRD documents.

### Product Description
TaskFlow is an AI-powered project management tool designed specifically for software development teams. It streamlines the process of breaking down project requirements into manageable tasks by automatically analyzing Product Requirements Documents (PRDs) and generating structured task hierarchies.

### Functional Requirements

#### Task Generation
- AI-powered task extraction from PRD documents
- Task hierarchy with epics, features, and individual tasks
- Automatic task dependency identification

#### Task Management
- Task assignment to team members
- Status tracking (todo, in progress, completed)
- Priority and effort estimation
"""
        logger.info("Using sample PRD content")
    
    # Generate tasks
    result = await generate_tasks(prd_content)
    
    # Print summary
    if result["status"] == "success":
        tasks = result["content"]
        print("\n✅ TASK GENERATION SUCCESSFUL")
        print(f"Total Tasks: {len(tasks.get('items', []))}")
        
        # Count by type
        task_types = {}
        for item in tasks.get("items", []):
            task_type = item.get("task_type")
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        # Print task type breakdown
        for task_type, count in task_types.items():
            print(f"{task_type.capitalize()}s: {count}")
        
    else:
        print("\n❌ TASK GENERATION FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main()) 