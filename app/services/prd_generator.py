"""
PRD Generator service for generating Product Requirements Documents.
"""
import logging
import os
import re
from typing import Dict, Any

from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.models.mistral import MistralChat

from .config import (
    PRD_MODEL_TYPE,
    PRD_MODEL_ID,
    ENABLE_DEBUG_MODE,
    ENABLE_SHOW_TOOL_CALLS,
    ENABLE_MARKDOWN
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PRDGeneratorService:
    """Service for generating Product Requirements Documents (PRD)."""

    def __init__(self, model_type: str = None, model_id: str = None):
        """
        Initialize the PRD Generator service.
        
        Args:
            model_type: The model provider to use ('groq', 'gemini', 'openai', or 'mistral')
            model_id: The model ID to use
        """
        self.model_type = model_type or PRD_MODEL_TYPE
        self.model_id = model_id or PRD_MODEL_ID
        
        # Initialize the model based on provider
        if self.model_type.lower() == "gemini":
            self.model = Gemini(id=self.model_id)
        elif self.model_type.lower() == "openai":
            self.model = OpenAIChat(id=self.model_id)
        elif self.model_type.lower() == "mistral":
            self.model = MistralChat(id=self.model_id)
        else:  # Default to groq
            self.model = Groq(id=self.model_id)
        
        logger.info(f"Initialized PRD Generator with {self.model_type} model (ID: {self.model_id})")

    async def generate_prd(self, brd_content: str, project_name: str = "Unnamed Project") -> Dict[str, Any]:
        """
        Generate a PRD based on a BRD.
        
        Args:
            brd_content: Content of the BRD document
            project_name: Name of the project
            
        Returns:
            Dictionary with PRD generation results, including content
            
        Raises:
            ValueError: If PRD generation fails
        """
        logger.info(f"Generating PRD for project: {project_name}")
        
        # Load PRD template for reference if available
        prd_template = ""
        try:
            template_path = os.path.join(os.path.dirname(__file__), "templates", "prd_template.md")
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    prd_template = f.read()
        except Exception as e:
            logger.warning(f"PRD template loading failed: {e}. Proceeding without template.")
        
        prd_agent = Agent(
            model=self.model,
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

            **NOTE: ENSURE FINAL OUTPUT ONLY CONTAINS MARKDOWN RESULT AND NOTHING ELSE. USE (```markdown) and (```) TO START AND END THE MARKDOWN RESULT.**
            """,
            add_datetime_to_instructions=True,
            reasoning=True,
            show_tool_calls=ENABLE_SHOW_TOOL_CALLS,
            debug_mode=ENABLE_DEBUG_MODE,
            markdown=ENABLE_MARKDOWN
        )
        
        try:
            prd_response = await prd_agent.arun()
            prd_content = prd_response.content.strip()

            # Extract content between ``` markers using regex
            match = re.search(r"```(markdown)?(.*?)```", prd_content, re.DOTALL)
            if match:
                prd_content = match.group(2).strip()
            
            logger.info(f"✅ Successfully generated PRD for {project_name}")
            
            return {
                "status": "success",
                "content": prd_content,
                "project_name": project_name
            }
            
        except Exception as e:
            logger.error(f"❌ PRD generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }