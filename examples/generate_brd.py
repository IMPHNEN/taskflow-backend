"""
BRD Generator Example

This example demonstrates how to use the BRDGeneratorService to generate 
a Business Requirements Document (BRD) based on project details.
"""
import asyncio
import logging
import os
import sys
from uuid import uuid4
from typing import Dict, Any

# Add the project root directory to the Python path if running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.brd_generator import BRDGeneratorService
from app.utils.ai_utils import save_markdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def generate_brd(project_details: Dict[str, Any], save_to_file: bool = True) -> Dict[str, Any]:
    """
    Generate a BRD from project details.
    
    Args:
        project_details: Dictionary with project information
        save_to_file: Whether to save the BRD to a file
        
    Returns:
        Dictionary with BRD generation results
    """
    logger.info(f"Generating BRD for project: {project_details.get('project_name', 'Unnamed Project')}")
    
    # Initialize the service
    brd_service = BRDGeneratorService()
    
    # Random UUID
    project_id = "28cf12ac-2f5e-4dd5-99b6-26a889f42a45"
    # project_id = str(uuid4())

    # Generate BRD
    result = await brd_service.generate_brd(project_details, project_id)
    
    # Check result
    if result["status"] == "success":
        logger.info(f"✅ BRD generation successful for {result['project_name']}")
        
        # Save to file if requested
        if save_to_file:
            # Save using the utility function with timestamp
            saved_path = save_markdown(result["content"], f"{result['project_name'].lower()}_brd")
            result["file_path"] = saved_path
    else:
        logger.error(f"❌ BRD generation failed: {result.get('error', 'Unknown error')}")
    
    return result


async def main():
    """Run the example with a sample project."""
    # Sample project details
    project_details = {
        "project_name": "TaskFlow",
        "project_description": "A project management tool for software developers that uses AI to generate tasks from PRD documents.",
        "start_date": "01/06/2023",
        "end_date": "31/08/2023"
    }
    
    # Generate BRD
    result = await generate_brd(project_details)
    
    # Print summary
    if result["status"] == "success":
        print("\n✅ BRD GENERATION SUCCESSFUL")
        print(f"Project: {result['project_name']}")
        print(f"BRD Length: {len(result['content'])} characters")
        print(f"Output files:")
        print(f" - {result.get('file_path', 'Not saved with timestamp')}")
        
        # Print the first 200 characters as preview
        preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
        print(f"\nPreview:\n{preview}")
    else:
        print("\n❌ BRD GENERATION FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main()) 