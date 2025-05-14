from agno.agent import Agent

from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.team import Team
from agno.tools.firecrawl import FirecrawlTools
import datetime
from agno.tools.tavily import TavilyTools
from dotenv import load_dotenv
load_dotenv(override=True)

# Model = OpenAIChat("gpt-4o-mini")
# Model = Groq("meta-llama/llama-4-scout-17b-16e-instruct")
market_research_model = Gemini("gemini-2.5-flash-preview-04-17")
market_analysis_model = OpenAIChat("gpt-4o-mini")
report_generator_model = OpenAIChat("gpt-4.1-mini-2025-04-14")
manager_model = OpenAIChat("gpt-4o-mini")

# Market Researcher agent that uses Tavily to search and Firecrawl to scrape data
market_researcher = Agent(
    name="MarketResearcher",
    model=market_research_model,
    role="Searches and scrapes data on existing platforms, features, and pricing",
    instructions = [
        "Given a project description, generate 3–5 relevant search terms to identify key competitors in the target market.",
        "Use Tavily to search for each term and compile a list of the top competitors.",
        "Use Firecrawl to map URLs from the identified competitor websites.",
        "Scrape each URL using Firecrawl, focusing on extracting detailed information about features, pricing plans, and unique selling points (USPs).",
        "Ensure that comprehensive data is collected for at least 5 major competitors.",
        "Emphasize extracting clear data points related to product/service features, pricing structure, and market positioning.",
        "Organize the extracted data in a clean, structured format suitable for comparison and analysis."
    ],

    #add crawl true if needed
    tools=[TavilyTools(), FirecrawlTools(scrape=True, mapping=True)],
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    markdown=True
)
# Market Analyzer agent that uses reasoning to analyze the collected data
market_analyzer = Agent(
    name="MarketAnalyzer",
    model=market_analysis_model,
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
    show_tool_calls=True
)

# Report Generator agent that creates a comprehensive market validation report
report_generator = Agent(
    name="ReportGenerator",
    model=report_generator_model,
    role="Creates a comprehensive market validation report in Markdown format",
    description=(
        "You are a professional report writer. Given analyzed market data, "
        "your goal is to create a comprehensive, well-structured market validation report."
    ),
    instructions = [
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
    show_tool_calls=True,
    markdown=True
)


# Market Validation Team that coordinates the entire process
market_validation_team = Team(
    name="MarketValidationTeam",
    mode="coordinate",
    model=manager_model,  # Using GPT-4o-mini for coordination
    members=[market_researcher, market_analyzer, report_generator],
    description="You are a market validation team. Given a project description, your goal is to produce a comprehensive market validation report.",
    instructions=[
        "First, ask the Market Researcher to search for and collect data on existing platforms, features, and pricing.",
        "The researcher should first use Tavily to find relevant competitor websites, then use Firecrawl to scrape detailed information.",
        "Then, ask the Market Analyzer to analyze the data and identify trends, gaps, and opportunities.",
        "ask the Report Generator to create a comprehensive market validation report.",
        """Ensure the final report includes : 
        1. competitor analysis with feature and pricing plans comparision.
        2. recommended USPs that not offered by competitors. 
        3. Future Market Projection.
        4. Revenue Stream and the Potention of the Revenue.
        5. Initial Cost Estimate to  produce the MVP(Minimum Viable Product).""",
        "Expected output: A comprehensive market validation report, avoid formal introductions, small talk, or unnecessary closing statements. Start directly with the content of the report. Do not use phrases like 'This report provides...' or 'feel free to ask'."
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
    import os
    os.makedirs("results", exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/{base_filename}_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filename


# Example usage
if __name__ == "__main__":
    project_description = input(str("Enter project description: "))
    time_before = datetime.datetime.now()
    print(f"Start Time: {time_before}")
    markdown_report = market_validation_team.run(project_description)
    time_after = datetime.datetime.now()
    print(f"End Time: {time_after}")
    print(f"Time taken: {time_after - time_before}")
    save_markdown(markdown_report.content, "market_validation_report")
    
    
    
    

