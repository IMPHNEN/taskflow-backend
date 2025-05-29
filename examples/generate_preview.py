"""
Preview Generator Example

This example demonstrates how to use the PreviewGeneratorService to generate 
a website preview/mockup using Lovable based on project details and BRD.
"""
import asyncio
import logging
import os
import sys
from uuid import uuid4
from typing import Dict, Any

# Add the project root directory to the Python path if running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.preview_generator import PreviewGeneratorService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def generate_preview(project_details: Dict[str, Any], brd_content: str) -> Dict[str, Any]:
    """
    Generate a website preview from project details and BRD.
    
    Args:
        project_details: Dictionary with project information
        brd_content: Business Requirements Document content
        
    Returns:
        Dictionary with preview generation results
    """
    logger.info(f"Generating preview for project: {project_details.get('name', 'Unnamed Project')}")
    
    # Initialize the service
    preview_service = PreviewGeneratorService()
    
    # Random UUID for user_id
    project_id = "28cf12ac-2f5e-4dd5-99b6-26a889f42a45"
    # project_id = str(uuid4())

    # Generate Preview
    result = await preview_service.generate_preview(project_details, brd_content, project_id)
    
    # Check result
    if result["status"] == "success":
        logger.info(f"✅ Preview generation successful for {result['project_name']}")
        logger.info(f"Preview URL: {result['preview_url']}")
    else:
        logger.error(f"❌ Preview generation failed: {result.get('error', 'Unknown error')}")
    
    return result


async def main():
    """Run the example with a sample project and BRD."""
    # Sample project details
    project_details = {
        "name": "TeleCare Connect",
        "objective": "A secure, HIPAA-compliant telemedicine platform that goes beyond video visits by integrating real-time vital-sign data from patients' home devices (e.g., blood pressure cuffs, pulse oximeters). Clinicians can set custom alerts, triage based on incoming data trends, and seamlessly escalate to in-person care when needed."
    }
    
    # Sample BRD content (shortened for example)
    with open("examples/data/sample_brd.md", "r") as file:
        brd_content = file.read()
    
    # Generate Preview
    result = await generate_preview(project_details, brd_content)
    
    # Print summary
    if result["status"] == "success":
        print("\n✅ PREVIEW GENERATION SUCCESSFUL")
        print(f"Project: {result['project_name']}")
        print(f"Preview URL: {result['preview_url']}")
    else:
        print("\n❌ PREVIEW GENERATION FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    # Note: Make sure to set LOVABLE_EMAIL and LOVABLE_PASSWORD environment variables
    if not os.getenv("LOVABLE_EMAIL") or not os.getenv("LOVABLE_PASSWORD"):
        print("⚠️  Warning: LOVABLE_EMAIL and LOVABLE_PASSWORD environment variables are required")
        print("Please set them in your .env file before running this example.")
        print("\nExample .env entries:")
        print("LOVABLE_EMAIL=your-email@example.com")
        print("LOVABLE_PASSWORD=your-password")
        print("\nThe preview generation will fail without these credentials.")
        print("However, the prompt generation part will still work.\n")
    
    asyncio.run(main()) 