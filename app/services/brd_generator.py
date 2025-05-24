"""
BRD Generator service for generating Business Requirements Documents.
"""
import json
import logging
import os
import re
from typing import Dict, Any

from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.models.mistral import MistralChat
from agno.models.openai.like import OpenAILike
from agno.memory.v2.schema import UserMemory

from .config import (
    BRD_MODEL_TYPE,
    BRD_MODEL_ID,
    ENABLE_DEBUG_MODE,
    ENABLE_SHOW_TOOL_CALLS,
    ENABLE_MARKDOWN,
    OPENAI_LIKE_BASE_URL,
    OPENAI_LIKE_API_KEY,
)
from .memory_storage_service import get_memory, get_storage

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BRDGeneratorService:
    """Service for generating Business Requirements Documents (BRD)."""

    def __init__(self, model_type: str = None, model_id: str = None):
        """
        Initialize the BRD Generator service.
        
        Args:
            model_type: The model provider to use ('groq', 'gemini', 'openai', 'openai_like', or 'mistral')
            model_id: The model ID to use
        """
        self.model_type = model_type or BRD_MODEL_TYPE
        self.model_id = model_id or BRD_MODEL_ID
        
        # Initialize the model based on provider
        if self.model_type.lower() == "gemini":
            self.model = Gemini(id=self.model_id)
        elif self.model_type.lower() == "openai":
            self.model = OpenAIChat(id=self.model_id)
        elif self.model_type.lower() == "mistral":
            self.model = MistralChat(id=self.model_id)
        elif self.model_type.lower() == "openai_like":
            self.model = OpenAILike(id=self.model_id, base_url=OPENAI_LIKE_BASE_URL, api_key=OPENAI_LIKE_API_KEY)
        else:  # Default to groq
            self.model = Groq(id=self.model_id)
        
        # Load BRD template for reference if available
        brd_template = ""
        try:
            template_path = os.path.join(os.path.dirname(__file__), "templates", "brd_template.md")
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    brd_template = f.read()
        except Exception as e:
            logger.warning(f"BRD template loading failed: {e}. Proceeding without template.")
        
        # Initialize Memory and Storage using singleton service
        self.memory = get_memory()
        self.storage = get_storage()

        
        self.agent = Agent(
            model=self.model,
            memory=self.memory,
            enable_agentic_memory=True,
            enable_user_memories=True,
            storage=self.storage,
            name="BRDGenerator",
            instructions=f"""
            You are TaskFlow, an expert business analyst. Based on the provided project information,
            create a comprehensive Business Requirements Document (BRD) in markdown format.
            
            BRD Template Reference:
            ```markdown
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


            **NOTE: ENSURE FINAL OUTPUT ONLY CONTAINS MARKDOWN RESULT AND NOTHING ELSE.YOU MUST USE (```markdown) and (```) TO START AND END THE MARKDOWN RESULT.**
            """,
            add_datetime_to_instructions=True,
            reasoning=True,
            show_tool_calls=ENABLE_SHOW_TOOL_CALLS,
            debug_mode=ENABLE_DEBUG_MODE,
            markdown=ENABLE_MARKDOWN
        )
            
        logger.info(f"Initialized BRD Generator with {self.model_type} model (ID: {self.model_id})")

    async def generate_brd(self, project_details: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive BRD based on project details.
        
        Args:
            project_details: Dictionary containing project information including:
                - project_name: Name of the project
                - project_description: Brief description of the project
                - start_date: Project start date (dd/mm/yyyy)
                - end_date: Project end date (dd/mm/yyyy)
            
        Returns:
            Dictionary with BRD generation results, including content
            
        Raises:
            ValueError: If BRD generation fails
        """
        logger.info(f"Generating BRD for: {project_details.get('project_name', 'Unnamed Project')}")
        
        # Convert project details to string for the prompt
        project_details_text = json.dumps(project_details, indent=2)
        
        try:
            brd_response = await self.agent.arun(f"""
            Project Details:
            {project_details_text}
            """, user_id=user_id, session_id=f"{user_id}_brd" if user_id else None)
            brd_content = brd_response.content.strip()

            # Extract content between ``` markers using regex
            match = re.search(r"```(?:markdown)?([\s\S]*?)```\s*$", brd_content, re.MULTILINE)
            if match:
                brd_content = match.group(1).strip()

            project_name = project_details.get('project_name', 'Unnamed Project')
            self.memory.add_user_memory(user_id=user_id, memory=UserMemory(
                memory=f"""
                Project BRD:
                ```markdown
                {brd_content}
                ```
                """,
                topics=["BRD", "Business Requirements Document"],
            ))
            logger.info(f"✅ Successfully generated BRD for {project_name}")
            
            return {
                "status": "success",
                "content": brd_content,
                "project_name": project_name
            }
            
        except Exception as e:
            logger.error(f"❌ BRD generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
