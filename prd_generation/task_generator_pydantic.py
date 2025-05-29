import os
import json
import logging
import re
from typing import List, Optional
import argparse
from pydantic import BaseModel, Field, model_validator, ConfigDict
from enum import Enum
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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TASKFLOW_MODEL_ID = "llama-3.3-70b-versatile"


class TaskType(str, Enum):
    EPIC = "epic"
    FEATURE = "feature"
    TASK = "task"


# ===== PYDANTIC MODELS =====
class BaseTaskItem(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "epic_1",
            "title": "Epic Title",
            "description": "Description of the epic",
            "task_type": "epic",
            "position": 1,
            "parent_id": None
        }
    })

    id: str
    title: str
    description: str
    task_type: TaskType
    status: str
    position: int
    parent_id: Optional[str] = None


class Epic(BaseTaskItem):
    @model_validator(mode="after")
    def must_be_epic(self):
        if self.task_type != TaskType.EPIC:
            raise ValueError('task_type must be "epic"')
        return self


class Feature(BaseTaskItem):
    @model_validator(mode="after")
    def must_be_feature(self):
        if self.task_type != TaskType.FEATURE:
            raise ValueError('task_type must be "feature"')
        return self


class Task(BaseTaskItem):
    estimated_hours: int
    dependencies: List[str]

    @model_validator(mode="after")
    def must_be_task(self):
        if self.task_type != TaskType.TASK:
            raise ValueError('task_type must be "task"')
        return self

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "task_1",
            "title": "Task Title",
            "description": "Short one or two sentence summary of the task.",
            "task_type": "task",
            "position": 1,
            "parent_id": "feature_1",
            "estimated_hours": 8,
            "dependencies": []
        }
    })


class TaskHierarchy(BaseModel):
    items: List[BaseTaskItem]

    @model_validator(mode="after")
    def validate_hierarchy(self):
        items = self.items

        # Collect all IDs by type
        epic_ids = {item.id for item in items if item.task_type == TaskType.EPIC}
        feature_items = [item for item in items if item.task_type == TaskType.FEATURE]
        task_items = [item for item in items if item.task_type == TaskType.TASK]
        feature_ids = {item.id for item in feature_items}

        # Validate parents
        for feature in feature_items:
            if feature.parent_id not in epic_ids:
                raise ValueError(f"Feature {feature.id} has invalid parent_id: {feature.parent_id}")

        for task in task_items:
            if task.parent_id not in feature_ids:
                raise ValueError(f"Task {task.id} has invalid parent_id: {task.parent_id}")

        return self


# ===== UTILITIES =====
def extract_json(content: str) -> dict:
    """Extract JSON from content that may contain markdown or extra text."""
    logger.info("🔍 Attempting to extract JSON from response...")
    json_match = re.search(r"```json\s*({.*?})\s*```", content, re.DOTALL)

    if json_match:
        logger.info("✅ Found JSON inside ```json block.")
        json_str = json_match.group(1).strip()
    else:
        logger.warning("⚠️ No markdown JSON block found, using raw content as-is.")
        json_str = content.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse extracted JSON: {e}\nRaw string:\n{json_str}")
        raise ValueError(f"Invalid JSON after extraction: {e}\nRaw JSON string:\n{json_str}")

os.environ["GOOGLE_API_KEY"] = "AIzaSyAmulVV5yjt6bCz9tKqPmceG8uq06bbfHg"

# ===== MAIN FUNCTION =====
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def generate_task_hierarchy(prd_file_path: str, model_name: str = "groq") -> dict:
    """
    Generate task hierarchy from PRD using Pydantic validation.
    
    Args:
        prd_file_path: Path to the PRD file
        
    Returns:
        Task hierarchy in dictionary format (validated)
        
    Raises:
        FileNotFoundError: If PRD file is not found
        ValueError: If task hierarchy generation fails
    """
    logger.info(f"📄 Reading PRD from: {prd_file_path}")

    if not os.path.isfile(prd_file_path):
        raise FileNotFoundError(f"File not found: {prd_file_path}")

    with open(prd_file_path, "r", encoding="utf-8") as f:
        prd_content = f.read()

    logger.info("🧠 Generating task hierarchy from PRD...")

    prompt = f"""
You are an expert technical project planner. Based on the Product Requirements Document (PRD) below, generate a structured, hierarchical task breakdown in JSON format that matches the database schema.

PRD:
\"\"\"{prd_content}\"\"\"


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
      "dependencies": []
    }}
  ]
}}

Guidelines:
- Output ONLY valid JSON.
- All items must contain: id, title, description, task_type, status, position, parent_id.
- Tasks must also contain: estimated_hours and dependencies.
- Use the format "epic_n", "feature_n", "task_n" for the `id` fields (e.g. epic_1, feature_2, task_3, etc).
- task_type must be one of: "epic", "feature", "task".
- Use integer values (1, 2, 3, ...) for `position`
"""
    
    if model_name == "gemini":
        from agno.models.google import Gemini
        model = Gemini(id="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY)
    else:
        model = Groq(id=TASKFLOW_MODEL_ID, api_key=GROQ_API_KEY)
    agent = Agent(
        model=model,
        name="TaskGenerator",
        instructions=prompt
    )

    response = agent.run()

    try:
        content = response.content.strip()
        raw_result = extract_json(content)

        # Validasi dengan Pydantic
        validated_data = TaskHierarchy(**raw_result)

        result_dict = validated_data.model_dump()

        # Simpan ke file
        with open("task_hierarchy.json", "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2)
        logger.info("✅ Successfully generated and validated task hierarchy.")
        return result_dict

    except Exception as e:
        logger.error(f"❌ Validation error: {e}\nRaw content:\n{content}")
        raise


# ===== CLI ENTRY POINT =====
# def main():
#     print("\n🧠 Generating task hierarchy from PRD...")
#     task_hierarchy = generate_task_hierarchy("prd.md")
#     print("🎉 Task hierarchy generation completed successfully.")
#     print("📁 Saved to: task_hierarchy.json")

def main():
    parser = argparse.ArgumentParser(description="Generate task hierarchy from PRD.")
    parser.add_argument("model", nargs="?", default="groq", help="Model to use: 'groq' (default) or 'gemini'")
    args = parser.parse_args()

    print(f"\n🧠 Generating task hierarchy from PRD using model: {args.model}...")
    task_hierarchy = generate_task_hierarchy("prd.md", model_name=args.model)
    print("🎉 Task hierarchy generation completed successfully.")
    print("📁 Saved to: task_hierarchy.json")


if __name__ == "__main__":
    main()