"""
BRD/PRD Generation Tool

This script generates Business Requirements Documents (BRD) and Product Requirements Documents (PRD)
using the Agno LLM platform with Groq's LLama-3 model. It takes user input about a project and
generates comprehensive documentation that follows industry standards.

Usage:
    python brd_generation.py [--skip-input] [--name PROJECT_NAME] [--description PROJECT_DESCRIPTION]
    [--brd-file BRD_FILE] [--prd-file PRD_FILE]
"""

import os
import json
import logging
import argparse
import sys
import time
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Agno modules
from agno.agent import Agent
from agno.models.groq import Groq

# === CONFIGURATION ===
# You can set your API key here or as an environment variable
# os.environ["GROQ_API_KEY"] = "your-api-key-here"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TASKFLOW_MODEL_ID = "llama-3.3-70b-versatile"

class BRDGenerator:
    """
    BRD Generator using Agno for document generation.
    
    This class handles the generation of Business Requirements Documents (BRD)
    based on user input about a project.
    """
    
    def __init__(self, api_key: Optional[str] = GROQ_API_KEY):
        """
        Initialize the BRD Generator.
        
        Args:
            api_key: API key for Groq. Defaults to environment variable.
                    
        Raises:
            ValueError: If no API key is provided or found in environment variables.
        """
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it as an environment variable or provide it directly.")
        
        self.model_id = TASKFLOW_MODEL_ID
        
        # Initialize model
        self.model = Groq(id=self.model_id, api_key=self.api_key)
    
    def get_project_details(self) -> Dict[str, Any]:
        """
        Collect detailed project information from user input.
        
        Returns:
            Dictionary containing project information including name, description,
            objectives, target audience, features, budget, timeline, etc.
        """
        print("\n===== PROJECT DETAILS INPUT =====")
        project_name = input("Enter project name: ")
        project_description = input("Enter brief project description: ")
        
        print("\nBusiness Objectives (Enter 'done' when finished):")
        business_objectives = []
        while True:
            objective = input("Enter a business objective: ")
            if objective.lower() == 'done':
                break
            business_objectives.append(objective)
            
        print("\nTarget Audience:")
        target_audience = input("Who is the target audience for this project? ")
        
        print("\nKey Features (Enter 'done' when finished):")
        key_features = []
        while True:
            feature = input("Enter a key feature: ")
            if feature.lower() == 'done':
                break
            key_features.append(feature)
            
        budget = input("\nProject budget (if known): ")
        timeline = input("Project timeline (e.g., 3 months): ")
        
        # Industry and competitors
        industry = input("\nIndustry sector: ")
        competitors = input("Known competitors (comma separated): ")
        
        # Project constraints
        constraints = input("\nAny project constraints (technical, regulatory, etc.): ")
        
        return {
            "project_name": project_name,
            "project_description": project_description,
            "business_objectives": business_objectives,
            "target_audience": target_audience,
            "key_features": key_features,
            "budget": budget,
            "timeline": timeline,
            "industry": industry,
            "competitors": competitors,
            "constraints": constraints
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def generate_brd(self, project_details: Dict[str, Any]) -> str:
        """
        Generate a comprehensive BRD based on project details.
        
        Args:
            project_details: Dictionary containing project information
            
        Returns:
            Complete BRD content in markdown format
            
        Raises:
            ValueError: If BRD generation fails
        """
        logger.info(f"Generating BRD for: {project_details['project_name']}")
        
        # Convert project details to string for the prompt
        project_details_text = json.dumps(project_details, indent=2)
        
        # Load BRD template for reference
        brd_template = ""
        try:
            with open("BRD_toko_kita.md", "r", encoding="utf-8") as f:
                brd_template = f.read()
        except FileNotFoundError:
            logger.warning("BRD template file not found. Proceeding without template.")
        
        brd_agent = Agent(
            model=self.model,
            name="BRDGenerator",
            instructions=f"""
            You are an expert business analyst. Based on the provided project information,
            create a comprehensive Business Requirements Document (BRD) in markdown format.
            
            Project Details:
            ```
            {project_details_text}
            ```
            
            BRD Template Reference:
            ```
            {brd_template}
            ```
            
            Your BRD should include the following sections:
            
            # BUSINESS REQUIREMENTS DOCUMENT (BRD)
            
            ## [Project Name]
            
            ## 1. Introduction
            [Provide a brief introduction to the project, including background and context]
            
            ## 2. Business Objectives
            [List the key business objectives that this project aims to achieve]
            
            ## 3. Project Scope
            [Define what is included and excluded from the scope of this project]
            
            ## 4. Functional Requirements
            [List and describe the functional requirements in a table format with priority levels]
            
            ## 5. Non-Functional Requirements
            [Define performance, security, scalability, and other quality requirements]
            
            ## 6. Project Constraints
            [List budget, timeline, and resource constraints]
            
            ## 7. Project Acceptance Criteria
            [Define what constitutes successful completion of the project]
            
            Make the BRD detailed, actionable, and specific to the project. Focus on clarity and practicality.
            Use the BRD template as a reference for structure and content, but adapt it to the specific project.
            
            Based on the project's industry, extrapolate potential market needs, competitors' features, and industry standards.
            Include these insights in your BRD to make it more comprehensive and realistic.
            """
        )
        
        brd_response = brd_agent.run()
        
        try:
            # Extract the BRD content
            brd_content = brd_response.content.strip()
            logger.info("Successfully generated BRD")
            return brd_content
            
        except Exception as e:
            logger.error(f"Failed to generate BRD: {e}")
            raise ValueError(f"Failed to generate BRD: {e}")
    
    def save_brd_to_file(self, brd_content: str, output_file: str = "brd.md") -> None:
        """
        Save the generated BRD to a markdown file.
        
        Args:
            brd_content: The BRD content in markdown format
            output_file: Path to save the BRD
            
        Raises:
            ValueError: If file saving fails
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(brd_content)
            logger.info(f"BRD saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save BRD to file: {e}")
            raise ValueError(f"Failed to save BRD to file: {e}")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def generate_prd_from_brd(brd_file_path: str) -> str:
    """
    Generate a PRD based on the BRD.
    
    Args:
        brd_file_path: Path to the BRD file
        
    Returns:
        Complete PRD content in markdown format
        
    Raises:
        FileNotFoundError: If BRD file is not found
        ValueError: If PRD generation fails
    """
    logger.info(f"Generating PRD from BRD: {brd_file_path}")
    
    if not os.path.isfile(brd_file_path):
        raise FileNotFoundError(f"BRD file not found: {brd_file_path}")
    
    with open(brd_file_path, "r", encoding="utf-8") as f:
        brd_content = f.read()
    
    # Try to load the PRD template for reference
    prd_template = ""
    try:
        with open("PRD_toko_kita.md", "r", encoding="utf-8") as f:
            prd_template = f.read()
    except FileNotFoundError:
        logger.warning("PRD template file not found. Proceeding without template.")
    
    agent = Agent(
        model=Groq(id=TASKFLOW_MODEL_ID, api_key=GROQ_API_KEY),
        name="PRDGenerator",
        instructions=f"""
        You are an expert product manager. Based on the provided Business Requirements Document (BRD),
        create a comprehensive Product Requirements Document (PRD) in markdown format.
        
        BRD:
        \"\"\"{brd_content}\"\"\"
        
        PRD Template Reference:
        \"\"\"{prd_template}\"\"\"
        
        Create a detailed PRD following the structure of the template provided. Your PRD should include these sections with similar formatting and level of detail:

        # PRODUCT REQUIREMENTS DOCUMENT (PRD)

        ## [Project Name]

        ### Introduction
        [Brief introduction based on the BRD]

        ### Product Description
        [Detailed description of the product]

        ### Product Objective
        [Key objectives from the BRD]

        ### Target User
        [Detailed breakdown of target users with demographics]

        ### Functional Requirements
        [Organize by feature categories, similar to the template]
        
        For each functional requirement, include:
        - Priority (High/Medium/Low)
        - Description
        - User Story (As a [user], I want to [action] so that [benefit])
        - Acceptance Criteria (bullets of testable requirements)

        ### Non-Functional Requirements
        [Include sections for Performance, Security, Scalability, Availability, Usability, Compatibility, Maintenance, etc.]

        ### User Interface Requirements
        [Key screens and UI components]

        ### Technical Requirements
        [System architecture, technology stack, etc.]

        ### Project Budget and Limitations
        [From the BRD]

        ### Project Acceptance Criteria
        [Clear criteria for project success]

        ### Schedule and Milestones
        [Break down into phases with estimated timeframes]

        ### Risk and Mitigation
        [Technical and business risks with mitigation strategies]

        ### Glossary
        [Technical terms and definitions]

        Make sure to:
        1. Use the same detailed format for functional requirements as seen in the template
        2. Include user stories and acceptance criteria for each feature
        3. Maintain consistent formatting throughout
        4. Be specific about technical implementation details
        5. Adapt the template structure to fit the specific project in the BRD
        """
    )
    
    prd_response = agent.run()
    
    try:
        # Extract the PRD content
        prd_content = prd_response.content.strip()
        logger.info("Successfully generated PRD")
        
        # Save the PRD to a file
        with open("prd.md", "w", encoding="utf-8") as f:
            f.write(prd_content)
        logger.info("PRD saved to prd.md")
        
        return prd_content
        
    except Exception as e:
        logger.error(f"Failed to generate PRD: {e}")
        raise ValueError(f"Failed to generate PRD: {e}")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def generate_task_hierarchy(prd_file_path: str) -> Dict[str, Any]:
    """
    Generate task hierarchy from PRD.
    
    Args:
        prd_file_path: Path to the PRD file
        
    Returns:
        Task hierarchy in JSON format
        
    Raises:
        FileNotFoundError: If PRD file is not found
        ValueError: If task hierarchy generation fails
    """
    logger.info(f"Reading PRD from: {prd_file_path}")

    if not os.path.isfile(prd_file_path):
        raise FileNotFoundError(f"File not found: {prd_file_path}")

    with open(prd_file_path, "r", encoding="utf-8") as f:
        prd_content = f.read()

    logger.info("Generating task hierarchy from PRD...")

    prompt = f"""
You are an expert technical project planner. Based on the Product Requirements Document (PRD) below, generate a structured implementation plan in JSON.

PRD:
\"\"\"{prd_content}\"\"\"

Output JSON format:
{{
  "epics": [
    {{
      "title": "Epic Title",
      "features": [
        {{
          "title": "Feature Title",
          "tasks": [
            {{
              "id": "task_001",
              "title": "Task Title",
              "description": "Short one or two sentence summary of the task.",
              "estimated_hours": 8,
              "priority": "high",  // or "medium", "low"
              "dependencies": ["task_000"]
            }}
          ]
        }}
      ]
    }}
  ]
}}

Guidelines:
- Output ONLY valid JSON (no prose or explanation).
- All keys must be present in every task.
- Use short string IDs: task_001, task_002, etc.
- Estimate realistic work hours.
- Set priority: high (urgent), medium (important), low (non-blocking).
- Include description for each task (1–2 concise sentences).
- Use task dependencies where appropriate.
"""

    agent = Agent(
        model=Groq(id=TASKFLOW_MODEL_ID, api_key=GROQ_API_KEY),
        name="TaskGenerator",
        instructions=prompt
    )

    response = agent.run()

    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)
        logger.info("✅ Successfully generated task hierarchy.")
        
        # Save the task hierarchy to a file
        with open("task_hierarchy.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        logger.info("Task hierarchy saved to task_hierarchy.json")
        
        return result
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse Agno response: {e}\nRaw content:\n{content}")
        raise ValueError(f"Agno returned invalid JSON: {str(e)}\nRaw Content:\n{content}")


def main():
    """
    Main function to run the BRD and PRD generation workflow.
    
    Parses command-line arguments and orchestrates the document generation process.
    """
    parser = argparse.ArgumentParser(
        description="Generate BRD and PRD based on project information",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--skip-input", action="store_true", 
                        help="Skip interactive input and use command line arguments")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--description", help="Project description")
    parser.add_argument("--brd-file", default="brd.md", 
                        help="BRD output file path")
    parser.add_argument("--prd-file", default="prd.md", 
                        help="PRD output file path")
    
    args = parser.parse_args()
    
    try:
        # Initialize BRD Generator
        generator = BRDGenerator()
        
        # Get project details
        if args.skip_input and args.name and args.description:
            project_details = {
                "project_name": args.name,
                "project_description": args.description,
                "business_objectives": [],
                "target_audience": "",
                "key_features": [],
                "budget": "",
                "timeline": "",
                "industry": "",
                "competitors": "",
                "constraints": ""
            }
        else:
            project_details = generator.get_project_details()
        
        # Generate BRD
        print("\nGenerating Business Requirements Document (BRD)...")
        brd_content = generator.generate_brd(project_details)
        
        # Save BRD to file
        brd_file = args.brd_file
        generator.save_brd_to_file(brd_content, brd_file)
        print(f"\nBRD generation completed successfully. Saved to: {brd_file}")
        
        # Generate PRD from BRD
        print("\nGenerating Product Requirements Document (PRD) from BRD...")
        prd_content = generate_prd_from_brd(brd_file)
        print(f"PRD generation completed successfully. Saved to: {args.prd_file}")
        
        # Generate task hierarchy from PRD
        print("\nGenerating task hierarchy from PRD...")
        task_hierarchy = generate_task_hierarchy(args.prd_file)
        print("Task hierarchy generation completed successfully. Saved to: task_hierarchy.json")
        
    except Exception as e:
        logger.error(f"Error during document generation: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()