"""
Preview Generator service for generating website mockups using Lovable.
"""
import logging
import os
import re
import asyncio
from typing import Dict, Any

from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.models.mistral import MistralChat
from agno.models.openai.like import OpenAILike
from agno.memory.v2.schema import UserMemory
from patchright.async_api import async_playwright

from .config import (
    DEFAULT_MODEL_TYPE,
    DEFAULT_MODEL_ID,
    ENABLE_DEBUG_MODE,
    ENABLE_SHOW_TOOL_CALLS,
    ENABLE_MARKDOWN,
    OPENAI_LIKE_BASE_URL,
    OPENAI_LIKE_API_KEY,
    LOVABLE_COOKIES,
    WS_CDP_ENDPOINT,
    DATA_DIR,
    BROWSER_ARGS,
    BROWSER_UA,
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
            self._model = Gemini(id=self.model_id)
        elif self.model_type.lower() == "openai":
            self._model = OpenAIChat(id=self.model_id)
        elif self.model_type.lower() == "mistral":
            self._model = MistralChat(id=self.model_id)
        elif self.model_type.lower() == "openai_like":
            self._model = OpenAILike(id=self.model_id, base_url=OPENAI_LIKE_BASE_URL, api_key=OPENAI_LIKE_API_KEY)
        else:  # Default to groq
            self._model = Groq(id=self.model_id)
        
        # Initialize Memory and Storage using singleton service
        self._memory = get_memory()
        self._storage = get_storage()

        # Initialize shared browser context
        self._playwright = None
        self._cdp_client = None
        self._context = None
        self._ping_task = None
        
        # Initialize the agent for query generation
        self._agent = Agent(
            model=self._model,
            memory=self._memory,
            enable_agentic_memory=True,
            enable_user_memories=True,
            storage=self._storage,
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

    @property
    async def _playwright(self):
        """Internal method to get or create playwright instance"""
        if self._playwright_instance is None:
            self._playwright_instance = await async_playwright().start()
        return self._playwright_instance

    async def _ping_cdp_server(self, cdp_client, interval=120):
        """Internal method to ping CDP server every interval seconds to prevent timeout using a separate context"""
        ping_context = None
        try:
            ping_context = await cdp_client.new_context()
            ping_page = await ping_context.new_page()
            while True:
                try:
                    await asyncio.sleep(interval)
                    # Simple ping by evaluating a basic expression
                    await ping_page.evaluate("1 + 1")
                except Exception as e:
                    break
        finally:
            if ping_context:
                await ping_context.close()

    async def _initialize_browser(self):
        """Internal method to initialize browser context if not already initialized"""
        if not self._context:
            pw = await self._playwright
            if WS_CDP_ENDPOINT:
                self._cdp_client = await pw.chromium.connect(
                    ws_endpoint=WS_CDP_ENDPOINT,
                    timeout=10000,
                    slow_mo=1000,
                    headers={
                        "User-Agent": BROWSER_UA,
                    }
                )
                self._context = await self._cdp_client.new_context()
                # Start ping task with CDP client
                self._ping_task = asyncio.create_task(self._ping_cdp_server(self._cdp_client))
            else:
                self._context = await pw.chromium.launch_persistent_context(
                    user_data_dir=DATA_DIR,
                    headless=False,
                    args=BROWSER_ARGS,
                    slow_mo=1000
                )

            # Parse and add cookies
            if LOVABLE_COOKIES:
                cookies = []
                for cookie in LOVABLE_COOKIES.split("; "):
                    name, value = cookie.split("=", 1)
                    cookies.append({
                        "name": name,
                        "value": value,
                        "domain": ".lovable.dev",
                        "path": "/"
                    })
                await self._context.add_cookies(cookies)

    async def _create_lovable_prompt(self, project_info: str, brd_content: str, user_id: str = None) -> str:
        """
        Internal method to create a prompt for Lovable AI tool based on project information and BRD.
        
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
        
        response = await self._agent.arun(
            prompt_input,
            user_id=user_id,
            session_id=f"{user_id}_preview" if user_id else None
        )
        
        return response.content.strip()

    async def _generate_mockup_with_patchright(self, lovable_prompt: str) -> Dict[str, Any]:
        """
        Internal method to generate mockup using patchright to interact with Lovable.
        
        Args:
            lovable_prompt: The prompt to send to Lovable
            
        Returns:
            Dictionary with mockup generation results
        """
        try:           
            # Create new page in existing context
            page = await self._context.new_page()
            
            try:
                logger.info("Visiting Lovable")
                await page.goto("https://lovable.dev/")
                
                logger.info("Filling query")
                await page.locator("#chatinput").fill(lovable_prompt)
                submit_button = page.locator("#chatinput-send-message-button")
                await submit_button.wait_for(state="visible", timeout=5000)
                await submit_button.click()

                # Check for daily limit message
                await page.wait_for_timeout(2000)
                limit_message = page.get_by_text("You have reached your daily messaging limit.")
                if await limit_message.is_visible(timeout=3000):
                    await page.close()
                    raise Exception("Daily messaging limit reached on Lovable")

                await page.wait_for_url(re.compile(r"https://lovable\.dev/projects/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))
                await page.wait_for_timeout(10000)
                loading_button = page.get_by_text("Spinning up preview...")
                logger.info("Waiting for generation to complete")
                
                try:
                    await loading_button.wait_for(state="hidden", timeout=500000)
                    logger.info("Generation complete")
                    await page.wait_for_timeout(2000)

                    error_button = page.get_by_role("button", name="Error Build unsuccessful")
                    if await error_button.is_visible():
                        logger.info("Build error detected, attempting fix...")
                        await error_button.click()
                        await page.get_by_role("button", name="Try to fix").first.click()
                        logger.info("Waiting for regeneration...")
                        await loading_button.wait_for(state="hidden", timeout=500000)
                        logger.info("Regeneration complete") 
                        await page.wait_for_timeout(2000)
                    
                    logger.info("Publishing preview")
                    await page.locator('//*[@id="publish-menu"]/span').click()
                    await page.locator("a[href='https://docs.lovable.dev/features/deploy'] + div > button").click()

                    logger.info("Waiting for preview to be published")
                    await page.wait_for_timeout(10000)

                    logger.info("Getting preview link")
                    preview_link = await page.locator('a[href^="https://preview--"]').first.get_attribute('href')
                    
                    await page.close()
                    return {
                        "status": "success",
                        "preview_url": preview_link,
                        "message": "Mockup generated successfully"
                    }
                    
                except Exception as e:
                    logger.info("Getting preview link")
                    preview_link = await page.locator('a[href^="https://preview--"]').first.get_attribute('href')
                    await page.close()
                    return {
                        "status": "success",
                        "preview_url": preview_link,
                        "message": "Mockup generated successfully"
                    }
                    
            except Exception as e:
                if page:
                    await page.close()
                raise e
            
        except Exception as e:
            logger.error(f"Patchright execution failed: {str(e)}")
            return {
                "status": "error", 
                "error": f"Browser automation failed: {str(e)}"
            }

    async def cleanup(self):
        """Cleanup browser resources"""
        if self._ping_task:
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass
            
        if self._context:
            await self._context.close()
            
        if self._cdp_client:
            await self._cdp_client.close()
            
        if self._playwright:
            await self._playwright.stop()

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
            # Initialize browser
            await self._initialize_browser()

            # Create project info string
            project_info = f"name: {project_details.get('name', 'Unnamed Project')}\nobjective/description: {project_details.get('objective', 'No description provided')}"
            
            # Step 1: Generate Lovable prompt
            lovable_prompt = await self._create_lovable_prompt(project_info, brd_content, user_id)
            logger.info(f"Generated Lovable prompt: {lovable_prompt[:100]}...")
            
            # Step 2: Generate mockup using patchright
            mockup_result = await self._generate_mockup_with_patchright(lovable_prompt)
            
            if mockup_result["status"] == "success":
                project_name = project_details.get('name', 'Unnamed Project')
                
                # Store in memory
                if user_id and self._memory:
                    self._memory.add_user_memory(user_id=user_id, memory=UserMemory(
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