"""
PRD Generator Example

This example demonstrates how to use the PRDGeneratorService to generate 
a Product Requirements Document (PRD) based on a BRD.
"""
import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add the project root directory to the Python path if running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.prd_generator import PRDGeneratorService
from app.utils.ai_utils import save_markdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def generate_prd(brd_content: str, project_name: str, save_to_file: bool = True) -> Dict[str, Any]:
    """
    Generate a PRD from BRD content.
    
    Args:
        brd_content: The content of a BRD document
        project_name: Name of the project
        save_to_file: Whether to save the PRD to a file
        
    Returns:
        Dictionary with PRD generation results
    """
    logger.info(f"Generating PRD for project: {project_name}")
    
    # Initialize the service
    prd_service = PRDGeneratorService()
    
    # Generate PRD
    result = await prd_service.generate_prd(brd_content, project_name)
    
    # Check result
    if result["status"] == "success":
        logger.info(f"✅ PRD generation successful for {result['project_name']}")
        
        # Save to file if requested
        if save_to_file:
            # Save using the utility function with timestamp
            saved_path = save_markdown(result["content"], f"{result['project_name'].lower()}_prd")
            result["file_path"] = saved_path
            
    else:
        logger.error(f"❌ PRD generation failed: {result.get('error', 'Unknown error')}")
    
    return result


async def main():
    """Run the example with a sample BRD."""
    project_name = "TaskFlow"
    
    # Sample BRD content - Normally you would load this from a file or generate it
    sample_brd_content = """# BUSINESS REQUIREMENTS DOCUMENT (BRD)

## TaskFlow

## 1. Introduction
TaskFlow is a project management tool for software developers that uses AI to generate tasks from PRD documents.

## 2. Business Objectives
- Streamline project planning process
- Reduce time spent on task breakdown
- Improve consistency in task creation

## 3. Project Scope
This project includes developing an AI-powered tool that can analyze PRD documents and generate structured task hierarchies.

## 4. Functional Requirements
| Priority | Requirement |
|----------|-------------|
| High     | AI-powered task generation |
| High     | Task hierarchy management |
| Medium   | Project visualization |

## 5. Non-Functional Requirements
- Performance: Task generation should complete within 30 seconds
- Scalability: Support projects with up to 1000 tasks
- Security: Ensure document privacy

## 6. Project Constraints
- Timeline: 3 months development time
- Budget: Limited developer resources
- Technology: Must integrate with existing tools

## 7. Project Acceptance Criteria
- Successful generation of tasks from sample PRD
- 90% accuracy in task identification
- Positive feedback from test users
"""
    
    # Try to load BRD from file if it exists
    try:
        with open(f"examples/output_{project_name.lower()}_brd.md", "r", encoding="utf-8") as f:
            brd_content = f.read()
        logger.info("Using BRD from existing file")
    except FileNotFoundError:
        # Use the sample BRD if no file is found
        brd_content = sample_brd_content
        logger.info("Using sample BRD content")
    
    # Generate PRD
    result = await generate_prd(brd_content, project_name)
    
    # Print summary
    if result["status"] == "success":
        print("\n✅ PRD GENERATION SUCCESSFUL")
        print(f"Project: {result['project_name']}")
        print(f"PRD Length: {len(result['content'])} characters")
        print(f"Output files:")
        print(f" - {result.get('file_path', 'Not saved with timestamp')}")
        print(f" - examples/output_{result['project_name'].lower()}_prd.md")
        
        # Print the first 200 characters as preview
        preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
        print(f"\nPreview:\n{preview}")
    else:
        print("\n❌ PRD GENERATION FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main()) 