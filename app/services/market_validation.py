"""
Market Validation service for analyzing market opportunities.
"""
import logging
import datetime
import os
import re
from typing import Dict, Any

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.mistral import MistralChat
from agno.tools.tavily import TavilyTools
from .firecrawl import FirecrawlTools

from .config import (
    MARKET_RESEARCH_MODEL_TYPE,
    MARKET_RESEARCH_MODEL_ID,
    MARKET_ANALYSIS_MODEL_TYPE,
    MARKET_ANALYSIS_MODEL_ID,
    REPORT_GENERATOR_MODEL_TYPE,
    REPORT_GENERATOR_MODEL_ID,
    MARKET_VALIDATION_MANAGER_MODEL_TYPE,
    MARKET_VALIDATION_MANAGER_MODEL_ID,
    ENABLE_DEBUG_MODE,
    ENABLE_SHOW_TOOL_CALLS,
    ENABLE_MARKDOWN
)
from ..utils.ai_utils import save_markdown

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketValidationService:
    """Service for performing market validation analysis."""

    def __init__(self):
        """Initialize the Market Validation service."""
        # Initialize models
        self._init_models()
        
        # Initialize agents
        self._init_agents()
    
    def _init_models(self):
        """Initialize the models for market validation."""
        # Get model types and IDs from config
        research_model_type = MARKET_RESEARCH_MODEL_TYPE
        analysis_model_type = MARKET_ANALYSIS_MODEL_TYPE
        report_model_type = REPORT_GENERATOR_MODEL_TYPE
        manager_model_type = MARKET_VALIDATION_MANAGER_MODEL_TYPE
        
        research_model_id = MARKET_RESEARCH_MODEL_ID
        analysis_model_id = MARKET_ANALYSIS_MODEL_ID
        report_model_id = REPORT_GENERATOR_MODEL_ID
        manager_model_id = MARKET_VALIDATION_MANAGER_MODEL_ID
        
        # Initialize research model
        if research_model_type.lower() == "openai":
            self.market_research_model = OpenAIChat(id=research_model_id)
        elif research_model_type.lower() == "groq":
            self.market_research_model = Groq(id=research_model_id)
        elif research_model_type.lower() == "mistral":
            self.market_research_model = MistralChat(id=research_model_id)
        else:  # Default to Gemini
            self.market_research_model = Gemini(id=research_model_id)
            
        # Initialize analysis model
        if analysis_model_type.lower() == "gemini":
            self.market_analysis_model = Gemini(id=analysis_model_id)
        elif analysis_model_type.lower() == "groq":
            self.market_analysis_model = Groq(id=analysis_model_id)
        elif analysis_model_type.lower() == "mistral":
            self.market_analysis_model = MistralChat(id=analysis_model_id)
        else:  # Default to OpenAI
            self.market_analysis_model = OpenAIChat(id=analysis_model_id)
            
        # Initialize report model
        if report_model_type.lower() == "gemini":
            self.report_generator_model = Gemini(id=report_model_id)
        elif report_model_type.lower() == "groq":
            self.report_generator_model = Groq(id=report_model_id)
        elif report_model_type.lower() == "mistral":
            self.report_generator_model = MistralChat(id=report_model_id)
        else:  # Default to OpenAI
            self.report_generator_model = OpenAIChat(id=report_model_id)
            
        # Initialize manager model
        if manager_model_type.lower() == "gemini":
            self.manager_model = Gemini(id=manager_model_id)
        elif manager_model_type.lower() == "groq":
            self.manager_model = Groq(id=manager_model_id)
        elif manager_model_type.lower() == "mistral":
            self.manager_model = MistralChat(id=manager_model_id)
        else:  # Default to OpenAI
            self.manager_model = OpenAIChat(id=manager_model_id)
        
        logger.info(f"Initialized Market Validation models: Research={research_model_type}, Analysis={analysis_model_type}, Report={report_model_type}, Manager={manager_model_type}")
    
    def _init_agents(self):
        """Initialize the agents for market validation."""
        # Market Researcher agent
        self.market_researcher = Agent(
            name="MarketResearcher",
            model=self.market_research_model,
            role="Searches and scrapes data on existing platforms, features, and pricing",
            instructions=[
                "Given a project description, generate 3–5 relevant search terms to identify key competitors in the target market.",
                "Use Tavily to search for each term and compile a list of the top competitors.",
                "Use Firecrawl to map URLs from the identified competitor websites.",
                "Scrape each URL using Firecrawl, focusing on extracting detailed information about features, pricing plans, and unique selling points (USPs).",
                "Ensure that comprehensive data is collected for at least 5 major competitors.",
                "Emphasize extracting clear data points related to product/service features, pricing structure, and market positioning.",
                "Organize the extracted data in a clean, structured format suitable for comparison and analysis."
            ],
            tools=[TavilyTools(), FirecrawlTools(scrape=True, mapping=True)],
            add_datetime_to_instructions=True,
            show_tool_calls=ENABLE_SHOW_TOOL_CALLS,
            debug_mode=ENABLE_DEBUG_MODE,
            markdown=ENABLE_MARKDOWN
        )
        
        # Market Analyzer agent
        self.market_analyzer = Agent(
            name="MarketAnalyzer",
            model=self.market_analysis_model,
            role="Analyzes market data and identifies trends, gaps, and opportunities",
            description=(
                "You are a market analysis expert. Given data on competitors, features, and pricing, "
                "your goal is to analyze the market landscape and identify opportunities for the project."
            ),
            instructions=[
                "Analyze the data collected by the Market Researcher to identify market trends and patterns.",
                "Compare features across different platforms to identify common offerings and unique differentiators.",
                "Analyze pricing strategies to understand market positioning and value propositions.",
                "Identify gaps in the market that could be potential opportunities for the project.",
                "Evaluate the competitive landscape to determine market saturation and entry barriers.",
                "Provide data-driven insights on market positioning and potential unique selling points.",
            ],
            reasoning=True,
            add_datetime_to_instructions=True,
            show_tool_calls=ENABLE_SHOW_TOOL_CALLS,
            debug_mode=ENABLE_DEBUG_MODE
        )
        
        # Report Generator agent
        self.report_generator = Agent(
            name="ReportGenerator",
            model=self.report_generator_model,
            role="Creates a comprehensive market validation report in Markdown format",
            description=(
                "You are a professional report writer. Given analyzed market data, "
                "your goal is to create a comprehensive, well-structured market validation report."
            ),
            instructions=[
                "Create a professional market validation report in Markdown format.",
                "Include an executive summary highlighting key findings and recommendations.",
                "Provide detailed competitor analysis with feature comparisons and pricing plans.",
                "Include a comparison table of at least 3–5 competitors, highlighting their strengths and weaknesses.",
                """Visualize the competitor comparison using a Mermaid chart:
                ```mermaid
                pie
                    title Competitor Mindshare
                    "Elastic Search" : 15.6
                    "Amazon Kendra" : 15.8
                    "Azure Search" : 14.3
                ```""",
                "Identify and recommend unique selling points (USPs) of the project that are not offered by competitors.",
                """Summarize USPs using a Mermaid chart:
                ```mermaid
                graph LR
                    A[Niche Industry Customization] --> B[Increased Adoption]
                    C[Enhanced User Analytics] --> D[Improved User Experience]
                    E[AI-Driven Personalization] --> F[Enhanced User Engagement]
                    G[Flexible Pricing Models] --> H[Broader Market Reach]
                ```""",
                "Provide a market projection for the next 3–5 years, including estimated market size and growth trends.",
                """Visualize market projection using a Mermaid chart:
                ```mermaid
                xychart-beta
                    title "Market Size Projection"
                    x-axis "Year" [2025, 2026, 2027, 2028, 2029, 2030]
                    y-axis "Market Size (Billion USD)" 0 --> 5.5
                    line [2.5, 2.875, 3.3, 3.8, 4.4, 5.0]
                ```""",
                "Define potential revenue streams for the project and estimate earning potential over 1–3 years.",
                """Summarize revenue stream projections using a Mermaid pie chart, example:
                ```mermaid
                    pie
                    title Revenue Streams
                    "Subscriptions": 40
                    "Marketplace Fees": 25
                    "Ads": 20
                    "Enterprise Licensing": 15
                ```""",
                "Estimate initial costs for building the project, including human resources, tools, and time required.",
                """Visualize estimated cost breakdown using a Mermaid flowchart, example:
                ```mermaid
                flowchart TD
                A[Project Cost Estimate] --> B[Human Resources]
                A --> C[Tools & Software]
                A --> D[Time Allocation]
                B --> B1[Developers - $20k]
                B --> B2[Designers - $10k]
                C --> C1[Cloud Services - $5k]
                C --> C2[APIs/Tools - $3k]
                D --> D1[3 Months Timeline]
                ```""",
                "Format the report with clear headings, subheadings, tables, and bullet points for readability.",
                "Ensure the report is comprehensive yet concise, focusing on actionable insights and business value."
            ],
            add_datetime_to_instructions=True,
            show_tool_calls=ENABLE_SHOW_TOOL_CALLS,
            debug_mode=ENABLE_DEBUG_MODE,
            markdown=ENABLE_MARKDOWN
        )
        
        # Market Validation Team
        self.team = Team(
            name="MarketValidationTeam",
            mode="coordinate",
            model=self.manager_model,
            members=[self.market_researcher, self.market_analyzer, self.report_generator],
            description="You are a market validation team. Given a project description, your goal is to produce a comprehensive market validation report.",
            instructions=[
                "First, ask the Market Researcher to search for and collect data on existing platforms, features, and pricing.",
                "The researcher should first use Tavily to find relevant competitor websites, then use Firecrawl to scrape detailed information.",
                "Then, ask the Market Analyzer to analyze the data and identify trends, gaps, and opportunities.",
                "Finally, ask the Report Generator to create a comprehensive market validation report.",
                """Ensure the final report includes: 
                1. competitor analysis with feature and pricing plans comparison.
                2. recommended USPs that not offered by competitors. 
                3. Future Market Projection.
                4. Revenue Stream and the Potential of the Revenue.
                5. Initial Cost Estimate to produce the MVP(Minimum Viable Product).""",
                "Expected output: A comprehensive market validation report, avoid formal introductions, small talk, or unnecessary closing statements. Start directly with the content of the report. Do not use phrases like 'This report provides...' or 'feel free to ask'. **USE (```) TO START AND END THE MARKDOWN RESULT.**"
            ],
            add_datetime_to_instructions=True,
            add_member_tools_to_system_message=True,
            enable_agentic_context=True,
            share_member_interactions=True,
            show_members_responses=True, 
            show_tool_calls=ENABLE_SHOW_TOOL_CALLS,
            debug_mode=ENABLE_DEBUG_MODE,
            markdown=ENABLE_MARKDOWN
        )
    
    async def run_market_validation(self, project_description: str) -> Dict[str, Any]:
        """
        Run the market validation process.
        
        Args:
            project_description: Description of the project to validate
            
        Returns:
            Dictionary with market validation results, including report and timing information
        """
        logger.info("🚀 Starting market validation for project...")
        
        start_time = datetime.datetime.now()
        logger.info(f"Start Time: {start_time}")
        
        try:
            # Run the market validation team
            response = await self.team.arun(project_description)
            
            end_time = datetime.datetime.now()
            time_taken = end_time - start_time
            logger.info(f"End Time: {end_time}")
            logger.info(f"Time taken: {time_taken}")
            
            # Save the report
            report_content = response.content
            # report_path = save_markdown(report_content, "market_validation_report")
        
            # Extract content between ``` markers using regex
            match = re.search(r"```(.*?)```", report_content, re.DOTALL)
            if match:
                report_content = match.group(1).replace("markdown", "").strip()
            
            return {
                "status": "success",
                "content": report_content,
                # "report_path": report_path,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "time_taken_seconds": time_taken.total_seconds()
            }
            
        except Exception as e:
            logger.error(f"❌ Market validation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": datetime.datetime.now().isoformat()
            }
