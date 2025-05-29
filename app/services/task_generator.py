"""
TaskGenerator service for generating task hierarchies from PRD.
"""
import logging
from typing import Dict, Any

from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.models.mistral import MistralChat
from agno.models.openai.like import OpenAILike
from agno.memory.v2.schema import UserMemory

from app.services.memory_storage_service import get_memory, get_storage

from .config import (
    TASK_MODEL_TYPE,
    TASK_MODEL_ID,
    ENABLE_DEBUG_MODE,
    ENABLE_SHOW_TOOL_CALLS,
    ENABLE_MARKDOWN,
    OPENAI_LIKE_BASE_URL,
    OPENAI_LIKE_API_KEY,
)
from .models import TaskHierarchy
from ..utils.ai_utils import extract_json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskGeneratorService:
    """Service for generating task hierarchies from PRD documents."""

    def __init__(self, model_type: str = None, model_id: str = None):
        """
        Initialize the TaskGenerator service.
        
        Args:
            model_type: The model provider to use ('groq', 'gemini', 'openai', 'openai_like', or 'mistral')
            model_id: The model ID to use
        """
        self.model_type = model_type or TASK_MODEL_TYPE
        self.model_id = model_id or TASK_MODEL_ID
        
        # Initialize the model based on provider
        if self.model_type.lower() == "gemini":
            self.model = Gemini(id=self.model_id)
        elif self.model_type.lower() == "openai":
            self.model = OpenAIChat(id=self.model_id)
        elif self.model_type.lower() == "openai_like":
            self.model = OpenAILike(id=self.model_id, base_url=OPENAI_LIKE_BASE_URL, api_key=OPENAI_LIKE_API_KEY)
        elif self.model_type.lower() == "mistral":
            self.model = MistralChat(id=self.model_id)
        else:  # Default to groq
            self.model = Groq(id=self.model_id)
        
        self.memory = get_memory()
        self.storage = get_storage()

        prompt = f"""
You are TaskFlow, an expert technical project planner. Based on the provided Product Requirements Document (PRD), generate a structured, hierarchical task breakdown in JSON format that matches the database schema.

Output JSON format:
{{
  "items": [
    {{
      "id": "epic_1",
      "title": "Epic Title",
      "description": "Description of the epic",
      "task_type": "epic",
      "position": 1,
      "parent_id": null
    }},
    {{
      "id": "feature_1",
      "title": "Feature Title",
      "description": "Description of the feature",
      "task_type": "feature",
      "position": 1,
      "parent_id": "epic_1"
    }},
    {{
      "id": "task_1",
      "title": "Task Title",
      "description": "Short one or two sentence summary of the task.",
      "task_type": "task",
      "position": 1,
      "parent_id": "feature_1",
      "estimated_hours": 8,
    }}
  ]
}}

Guidelines:
- Output ONLY valid JSON.
- All items must contain: id, title, description, task_type, position, parent_id.
- Tasks must also contain: estimated_hours and dependencies.
- Use the format "epic_n", "feature_n", "task_n" for the `id` fields (e.g. epic_1, feature_2, task_3, etc).
- task_type must be one of: "epic", "feature", "task".
- Use integer values (1, 2, 3, ...) for `position`
"""
        
        self.agent = Agent(
            model=self.model,
            name="TaskGenerator",
            instructions=prompt,
            add_datetime_to_instructions=True,
            reasoning=True,
            show_tool_calls=ENABLE_SHOW_TOOL_CALLS,
            debug_mode=ENABLE_DEBUG_MODE,
            markdown=ENABLE_MARKDOWN
        )
            
        logger.info(f"Initialized Task Generator with {self.model_type} model (ID: {self.model_id})")

    async def generate_tasks(self, prd_content: str, user_id: str = None) -> Dict[str, Any]:
        """
        Generate task hierarchy from PRD content.
        
        Args:
            prd_content: Content of the PRD document
            
        Returns:
            Task hierarchy in dictionary format (validated)
            
        Raises:
            ValueError: If task hierarchy generation fails
        """
        logger.info("🧠 Generating task hierarchy from PRD...")

        response = await self.agent.arun(
            f"""
            PRD:
            ```markdown
            {prd_content}
            ```
            """,
            user_id=user_id,
            session_id=f"{user_id}_task_generator" if user_id else None
        )

        try:
            content = response.content.strip()
            raw_result = extract_json(content)

            # Validate with Pydantic
            validated_data = TaskHierarchy(**raw_result)
            result_dict = validated_data.model_dump()

            self.memory.add_user_memory(
                user_id=user_id,
                memory=UserMemory(
                    memory=f"Project Tasks: {result_dict}",
                    topics=["Task Hierarchy", "Generated Tasks", "Tasks"]
                )
            )

            # Save to file (optional, for debugging)
            # save_to_file(result_dict, "task_hierarchy.json")
            
            logger.info("✅ Successfully generated and validated task hierarchy.")
            return result_dict

        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            raise ValueError(f"Failed to generate task hierarchy: {str(e)}")
