"""
Complete document generation flow example:
BRD -> PRD -> Tasks -> Market Validation

This example demonstrates the complete workflow of:
1. Generating a Business Requirements Document (BRD)
2. Creating a Product Requirements Document (PRD) from the BRD
3. Generating a task hierarchy from the PRD
4. Performing market validation analysis
"""
import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any

# Add the project root directory to the Python path if running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.brd_generator import BRDGeneratorService
from app.services.prd_generator import PRDGeneratorService
from app.services.task_generator import TaskGeneratorService
from app.services.market_validation import MarketValidationService
from app.utils.ai_utils import save_markdown, save_to_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_full_document_flow(project_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete document generation flow.
    
    Args:
        project_details: Dictionary containing project information
        
    Returns:
        Dictionary with all results from each step
    """
    results = {}
    project_name = project_details.get('project_name', 'Unnamed Project')
    
    # Store output paths
    output_paths = {
        "brd": None,
        "prd": None,
        "tasks": None,
        "market_validation": None,
    }
    
    logger.info(f"🚀 Starting complete document generation flow for: {project_name}")
    
    # Step 1: Generate BRD
    logger.info("Step 1: Generating Business Requirements Document (BRD)")
    brd_service = BRDGeneratorService()
    brd_result = await brd_service.generate_brd(project_details)
    
    if brd_result["status"] != "success":
        logger.error(f"❌ BRD generation failed: {brd_result.get('error', 'Unknown error')}")
        return {"status": "error", "stage": "brd_generation", "error": brd_result.get("error")}
    
    # Save BRD with timestamp
    brd_path = save_markdown(brd_result["content"], f"{project_name.lower()}_brd")
    output_paths["brd"] = brd_path
    
    results["brd"] = brd_result
    logger.info(f"✅ BRD generated successfully: {len(brd_result['content'])} characters")
    
    # Step 2: Generate PRD from BRD
    logger.info("Step 2: Generating Product Requirements Document (PRD)")
    prd_service = PRDGeneratorService()
    prd_result = await prd_service.generate_prd(brd_result["content"], project_name)
    
    if prd_result["status"] != "success":
        logger.error(f"❌ PRD generation failed: {prd_result.get('error', 'Unknown error')}")
        return {
            "status": "error",
            "stage": "prd_generation",
            "error": prd_result.get("error"),
            "brd_result": brd_result
        }
    
    # Save PRD with timestamp
    prd_path = save_markdown(prd_result["content"], f"{project_name.lower()}_prd")
    output_paths["prd"] = prd_path
    
    results["prd"] = prd_result
    logger.info(f"✅ PRD generated successfully: {len(prd_result['content'])} characters")
    
    # Step 3: Generate tasks from PRD
    logger.info("Step 3: Generating Task Hierarchy")
    task_service = TaskGeneratorService()
    
    try:
        task_result = await task_service.generate_tasks(prd_result["content"])
        
        # Save tasks with timestamp
        tasks_path = save_to_file(task_result, f"{project_name.lower()}_tasks")
        output_paths["tasks"] = tasks_path
        
        results["tasks"] = {
            "status": "success",
            "content": task_result
        }
        task_count = len(task_result.get("items", []))
        logger.info(f"✅ Task hierarchy generated successfully: {task_count} tasks")
        
    except Exception as e:
        logger.error(f"❌ Task generation failed: {str(e)}")
        return {
            "status": "error",
            "stage": "task_generation",
            "error": str(e),
            "brd_result": brd_result,
            "prd_result": prd_result
        }
    
    # Step 4: Market Validation (optional)
    logger.info("Step 4: Performing Market Validation")
    market_service = MarketValidationService()
    
    try:
        market_result = await market_service.run_market_validation(project_details["project_description"])
        results["market_validation"] = market_result
        
        # The service already saves the report with timestamp, just grab the path
        if market_result["status"] == "success":
            market_result_path = save_markdown(market_result["content"] , f"{project_name.lower()}_market_validation")
            output_paths["market_validation"] = market_result_path
                
            logger.info(f"✅ Market validation completed: {len(market_result.get('content', ''))} characters")
            logger.info(f"✅ Market validation report saved to: {market_result_path}")
            
    except Exception as e:
        logger.error(f"❌ Market validation failed: {str(e)}")
        # Continue with the flow even if market validation fails
        results["market_validation"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Return combined results
    logger.info("🎉 Complete document generation flow finished successfully!")
    results["status"] = "success"
    results["output_paths"] = output_paths
    return results


async def main():
    """Run the example with a sample project."""
    # Sample project details
    project_details = {
        "project_name": "TaskFlow",
        "project_description": "A project management tool for software developers that uses AI to generate tasks from PRD documents.",
        "start_date": "01/06/2025",
        "end_date": "31/08/2025"
    }
    
    # Run the complete flow
    results = await run_full_document_flow(project_details)
    
    # Print summary of results
    if results["status"] == "success":
        print("\n🎉 DOCUMENT GENERATION FLOW COMPLETED SUCCESSFULLY!\n")
        
        print("📄 BRD Length:", len(results["brd"]["content"]))
        print("📄 PRD Length:", len(results["prd"]["content"]))
        print("📋 Tasks Generated:", len(results["tasks"]["content"]["items"]))
        
        if results.get("market_validation", {}).get("status") == "success":
            print("📊 Market Validation Report Length:", len(results["market_validation"]["content"]))
        else:
            print("⚠️ Market Validation:", results.get("market_validation", {}).get("error", "Failed"))
        
        print("\n📁 OUTPUT FILES:")
        for doc_type, path in results["output_paths"].items():
            if path:
                print(f" - {doc_type.upper()}: {path}")
                print(f"   Example copy: examples/output_{project_details['project_name'].lower()}_{doc_type}.{'md' if doc_type != 'tasks' else 'json'}")
            
        # Save example output
        with open("results/output_example.json", "w") as f:
            # Convert to serializable format
            serializable_results = {
                "brd": {"content_length": len(results["brd"]["content"])},
                "prd": {"content_length": len(results["prd"]["content"])},
                "tasks": {"count": len(results["tasks"]["content"]["items"])},
                "market_validation": {"status": results.get("market_validation", {}).get("status")},
                "output_paths": results["output_paths"]
            }
            json.dump(serializable_results, f, indent=2)
    else:
        print(f"\n❌ DOCUMENT GENERATION FLOW FAILED AT STAGE: {results.get('stage', 'Unknown')}")
        print(f"Error: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main()) 