"""
Market Validation Example

This example demonstrates how to use the MarketValidationService to perform
market research and validation for a project.
"""
import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add the project root directory to the Python path if running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.market_validation import MarketValidationService
from app.utils.ai_utils import save_markdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_market_validation(project_description: str, save_report: bool = True) -> Dict[str, Any]:
    """
    Run market validation for a project description.
    
    Args:
        project_description: Description of the project
        save_report: Whether to save an additional copy of the report (the service itself saves one)
        
    Returns:
        Dictionary with market validation results
    """
    logger.info("Starting market validation")
    
    # Initialize the service
    market_service = MarketValidationService()
    
    try:
        # Run market validation
        result = await market_service.run_market_validation(project_description)
        
        logger.info(f"✅ Market validation {'completed successfully' if result['status'] == 'success' else 'failed'}")
        
        # Save an additional copy with more descriptive filename if successful
        if result["status"] == "success" and save_report and "content" in result:
            # Service already saves the report, but we can save an additional copy with a better name
            path_saved = save_markdown(result["content"], "market_validation_report")
            result["report_path"] = path_saved
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Market validation failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


async def main():
    """Run the example with a sample project description."""
    # Project description
    project_description = """
    TaskFlow is an AI-powered project management tool designed specifically for software development teams. 
    It streamlines the process of breaking down project requirements into manageable tasks by automatically 
    analyzing Product Requirements Documents (PRDs) and generating structured task hierarchies.
    
    Key features:
    - AI-powered task extraction from PRD documents
    - Task hierarchy with epics, features, and individual tasks
    - Automatic task dependency identification
    - Task assignment to team members
    - Status tracking (todo, in progress, completed)
    - Priority and effort estimation
    """
    
    # Run market validation
    result = await run_market_validation(project_description)
    
    # Print summary
    if result["status"] == "success":
        print("\n✅ MARKET VALIDATION SUCCESSFUL")
        print(f"Report Length: {len(result.get('content', ''))} characters")
        print(f"Time Taken: {result.get('time_taken_seconds', 0):.2f} seconds")
        
        # Print the first 200 characters as preview
        preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
        print(f"\nPreview:\n{preview}")
    else:
        print("\n❌ MARKET VALIDATION FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main()) 