"""
Preview Generator service for generating website mockups using Lovable.
"""
import logging
import os
from typing import Dict, Any

import notte
from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.models.mistral import MistralChat
from agno.models.openai.like import OpenAILike
from agno.memory.v2.schema import UserMemory

from .config import (
    DEFAULT_MODEL_TYPE,
    DEFAULT_MODEL_ID,
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


class PreviewGeneratorService:
    """Service for generating website mockups using Lovable."""

    def __init__(self, model_type: str = None, model_id: str = None):
        """
        Initialize the Preview Generator service.
        
        Args:
            model_type: The model provider to use ('groq', 'gemini', 'openai', 'openai_like', or 'mistral')
            model_id: The model ID to use
        """
        self.model_type = model_type or DEFAULT_MODEL_TYPE
        self.model_id = model_id or DEFAULT_MODEL_ID
        
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
        
        # Initialize Memory and Storage using singleton service
        self.memory = get_memory()
        self.storage = get_storage()

        # Lovable credentials
        self.lovable_email = os.getenv("LOVABLE_EMAIL")
        self.lovable_password = os.getenv("LOVABLE_PASSWORD")
        
        if not self.lovable_email or not self.lovable_password:
            logger.warning("Lovable credentials not found in environment variables")
        
        # Initialize notte agent for browser automation
        self.notte_agent = notte.Agent(
            reasoning_model="openrouter/google/gemma-3-27b-it",
            max_steps=20,
            use_vision=False,
            headless=True,  # Set to True for production
            chrome_args=[
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--disable-media-src",
                "--blink-settings=imagesEnabled=false",
                "--disable-features=HardwareMediaKeyHandling,GlobalMediaControls",
                "--disable-accelerated-video-decode",
                "--disable-gpu",
                "--start-maximized",
            ],
            # web_security=True,
        )
        
        self.agent = Agent(
            model=self.model,
            memory=self.memory,
            enable_agentic_memory=True,
            enable_user_memories=True,
            storage=self.storage,
            name="PreviewGenerator",
            instructions="""
            You are a highly skilled Prompt Engineer tasked with crafting a precise and actionable prompt for the Lovable AI tool, which generates website mockups.
            
            Your task is to create a clear, well-structured prompt that will be processed directly by the Lovable AI tool.
            The prompt should be specific, design-focused, and suitable for a modern business homepage.
            
            Key requirements:
            1. Emphasize usability, aesthetic appeal, and functional clarity
            2. Include specific design elements based on the project context
            3. Consider the target audience and business objectives
            4. Make the prompt actionable and clear for the AI tool
            
            Based on the project information and business requirements, generate a comprehensive prompt that will result in an effective website mockup.
            
            **NOTE: RETURN ONLY THE PROMPT TEXT WITHOUT ANY ADDITIONAL EXPLANATION OR FORMATTING.**
            """,
            add_datetime_to_instructions=True,
            show_tool_calls=ENABLE_SHOW_TOOL_CALLS,
            debug_mode=ENABLE_DEBUG_MODE,
            markdown=ENABLE_MARKDOWN
        )
            
        logger.info(f"Initialized Preview Generator with {self.model_type} model (ID: {self.model_id})")

    async def create_lovable_prompt(self, project_info: str, brd_content: str, user_id: str = None) -> str:
        """
        Create a prompt for Lovable AI tool based on project information and BRD.
        
        Args:
            project_info: Project information string
            brd_content: Business Requirements Document content
            user_id: User ID for memory tracking
            
        Returns:
            Generated prompt for Lovable AI tool
        """
        
        prompt_input = f"""
        Project Context:
        ```
        {project_info}
        ```
        
        Business Requirements Document:
        ```markdown
        {brd_content}
        ```
        
        From the Project Context and Business Requirements Document, generate a Prompt for an AI tool called Lovable that will generate mockups for a website.
        """
        
        response = await self.agent.arun(
            prompt_input,
            user_id=user_id,
            session_id=f"{user_id}_preview" if user_id else None
        )
        
        return response.content.strip()

    async def generate_mockup_with_notte(self, lovable_prompt: str) -> Dict[str, Any]:
        """
        Generate mockup using notte agent to interact with Lovable.
        
        Args:
            lovable_prompt: The prompt to send to Lovable
            
        Returns:
            Dictionary with mockup generation results
        """
        if not self.lovable_email or not self.lovable_password:
            raise ValueError("Lovable credentials not configured")
        
        # Lovable automation task template
        task_template = """
---

### Prompt for Lovable Agent – Website Mockup Request

**Objective:**  
Log in to Lovable using the provided email and password, then request a **website mockup** based on the given query and requirements.

---

### Step 1: Log In

- Go to the Lovable website.
- Use the credentials below to log in:

  - **Email:**'{email}'  
  - **Password:**'{password}'

**Important:** Do **not** use "Sign in with Google" or "Sign in with GitHub". Use only the Email and Password fields.

### Step 2: Sign in

- Click the Sign in Button
- Check if you are logged in by checking if there is the '{email}' in the top-right corner.

if you are not logged in, try to login again.

---

### Step 3: Submit the Mockup Request

- After logging in, locate the input field for mockup requests.
- Submit the following query:

{query}

---

### Step 4: Wait for the Draft

- Wait **180,000 milliseconds (180 seconds)** for the mockup draft to generate.
- If the draft is not ready, wait an additional **180,000 milliseconds**.
- Continue waiting in 180-second intervals until the mockup is ready.

---

### Step 5: Output the Result

  Once the mockup is ready:
- Click the **Publish** button (top-right corner).
- After that there will be a Popup in the top right corner, click on the **Publish** button in the popup.
- Wait **30,000 milliseconds (30 seconds)** for the mockup to be published.
- If successful, the button label will change from **Publish** to **Update**.
- **Return only the preview link (https://preview--[project-name].lovable.app/)** of the published mockup.

**Important:** The site will show you the website but ITS NOT PUBLISHED YET, you need to publish it first.
**Important:** Make sure to check if the website is published before returning the link.
**Important:** Do **not** include any additional text or context. Return only the preview link.

---

**Important Notes:**  
Ensure the submitted query is clear, design-focused, and suitable for a modern business homepage. Emphasize usability, aesthetic appeal, and functional clarity.  
If the input query is unclear or ambiguous, feel free to **rephrase it** to better guide the agentic system on Lovable toward generating an optimal mockup.

---
"""
        
        # Format the task with credentials and prompt
        task = task_template.format(
            email=self.lovable_email,
            password=self.lovable_password,
            query=lovable_prompt
        )

        try:
            # Run the notte agent asynchronously
            result = await self.notte_agent.arun(task=task, url="https://lovable.dev/login")
            
            # Parse the result
            if result and hasattr(result, 'answer'):
                preview_url = result.answer
                if preview_url and preview_url.startswith("https://preview--"):
                    return {
                        "status": "success",
                        "preview_url": preview_url,
                        "message": "Mockup generated successfully"
                    }
            
            return {
                "status": "error",
                "error": "Failed to generate or publish mockup",
                "raw_result": str(result) if result else None
            }
            
        except Exception as e:
            logger.error(f"Notte agent execution failed: {str(e)}")
            return {
                "status": "error", 
                "error": f"Browser automation failed: {str(e)}"
            }

    async def generate_preview(self, project_details: Dict[str, Any], brd_content: str, user_id: str = None) -> Dict[str, Any]:
        """
        Generate a website preview/mockup based on project details and BRD.
        
        Args:
            project_details: Dictionary containing project information
            brd_content: Business Requirements Document content
            user_id: User ID for memory tracking
            
        Returns:
            Dictionary with preview generation results
            
        Raises:
            ValueError: If preview generation fails
        """
        logger.info(f"Generating preview for: {project_details.get('name', 'Unnamed Project')}")
        
        try:
            # Create project info string
            project_info = f"name: {project_details.get('name', 'Unnamed Project')}\nobjective/description: {project_details.get('objective', 'No description provided')}"
            
            # Step 1: Generate Lovable prompt
            lovable_prompt = await self.create_lovable_prompt(project_info, brd_content, user_id)
            logger.info(f"Generated Lovable prompt: {lovable_prompt[:100]}...")
            
            # Step 2: Generate mockup using notte
            mockup_result = await self.generate_mockup_with_notte(lovable_prompt)
            
            if mockup_result["status"] == "success":
                project_name = project_details.get('name', 'Unnamed Project')
                
                # Store in memory
                if user_id and self.memory:
                    self.memory.add_user_memory(user_id=user_id, memory=UserMemory(
                        memory=f"""
                        Project Preview Generated:
                        Project: {project_name}
                        Preview URL: {mockup_result['preview_url']}
                        Lovable Prompt: {lovable_prompt}
                        """,
                        topics=["Preview", "Mockup", "Website"],
                    ))
                
                logger.info(f"✅ Successfully generated preview for {project_name}")
                
                return {
                    "status": "success",
                    "preview_url": mockup_result["preview_url"],
                    "project_name": project_name
                }
            else:
                return mockup_result
                
        except Exception as e:
            logger.error(f"❌ Preview generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 