from agno.agent import Agent

from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.team import Team
from agno.tools.firecrawl import FirecrawlTools
import datetime
from agno.tools.tavily import TavilyTools

Model = Gemini("gemini-2.5-flash-preview-04-17")

# Market Researcher agent that uses Tavily to search and Firecrawl to scrape data
market_researcher = Agent(
    name="MarketResearcher",
    model=Model,
    role="Searches and scrapes data on existing platforms, features, and pricing",
    instructions=[
        "Given a project description, first generate 3-5 search terms to find key competitors in this market.",
        "Use Tavily to search for each term and identify the top competitors in the market space.",
        "Then use Firecrawl to scrape data from competitor websites, focusing on features, pricing, and unique selling points.",
        "Collect comprehensive data on at least 5 major competitors in the market space.",
        "Focus on extracting specific information about features, pricing plans, and market positioning.",
        "Organize the collected data in a structured format for analysis.",
    ],
    #add crawl true if needed
    tools=[TavilyTools(), FirecrawlTools(scrape=True)],
    add_datetime_to_instructions=True,
)
# Market Analyzer agent that uses reasoning to analyze the collected data
market_analyzer = Agent(
    name="MarketAnalyzer",
    model=Model,
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
    reasoning=True,  # Enable Agno's reasoning capabilities
    add_datetime_to_instructions=True,
)

# Report Generator agent that creates a comprehensive market validation report
report_generator = Agent(
    name="ReportGenerator",
    model=Model,
    role="Creates a comprehensive market validation report in Markdown format",
    description=(
        "You are a professional report writer. Given analyzed market data, "
        "your goal is to create a comprehensive, well-structured market validation report."
    ),
    instructions=[
        "Create a professional market validation report in Markdown format.",
        "Include an executive summary highlighting key findings and recommendations.",
        "Provide detailed competitor analysis with feature comparisons and pricing plans.",
        "Include a section on market gaps and opportunities identified during analysis.",
        "Recommend unique selling points (USPs) for the project based on the market analysis.",
        "Format the report with clear headings, tables, and bullet points for readability.",
        "Ensure the report is comprehensive yet concise, focusing on actionable insights.",
    ],
    add_datetime_to_instructions=True,
)

# Market Validation Team that coordinates the entire process
market_validation_team = Team(
    name="MarketValidationTeam",
    mode="coordinate",
    model=Model,  # Using GPT-4o-mini for coordination
    members=[market_researcher, market_analyzer, report_generator],
    description="You are a market validation team. Given a project description, your goal is to produce a comprehensive market validation report.",
    instructions=[
        "First, ask the Market Researcher to search for and collect data on existing platforms, features, and pricing.",
        "The researcher should first use Tavily to find relevant competitor websites, then use Firecrawl to scrape detailed information.",
        "Then, ask the Market Analyzer to analyze the data and identify trends, gaps, and opportunities.",
        "Finally, ask the Report Generator to create a comprehensive market validation report.",
        "Ensure the final report includes competitor analysis, feature comparisons, pricing plans, and recommended USPs.",
    ],
    add_datetime_to_instructions=True,
    add_member_tools_to_system_message=True,
    enable_agentic_context=True,  # Allow the team to maintain a shared context
    share_member_interactions=True,  # Share all member responses with subsequent member requests
    show_members_responses=True,
    show_tool_calls=True,
    markdown=True,
)

def save_markdown(markdown_content, base_filename):
    """
    Save markdown content to a file with a timestamp in the filename.
    
    Args:
        markdown_content (str): The markdown content to save
        base_filename (str): The base name of the file without extension
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filename


# Example usage
if __name__ == "__main__":
    project_description = """
    Search as a Service project, service that provide search results like marketplace product search.
    """
    markdown_report = market_validation_team.run(project_description)
    save_markdown(markdown_report.content, "./result/market_validation_report")
    
    

