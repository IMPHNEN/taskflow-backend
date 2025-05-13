import json
import datetime
import asyncio
import os

from agno.agent import Agent
from agno.team import Team

from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

from agno.models.groq import Groq

from dotenv import load_dotenv
import re
load_dotenv()

github_username = "username_github"
with open('prd.md', 'r') as file:
    prd_content = file.read()
with open('task_hierarchy.json', 'r') as file:
    tasks = json.load(file)

Model = Groq("llama-3.3-70b-versatile")

token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Please set GITHUB_TOKEN in env (see Step 2)")

if os.name == 'nt':  # Windows
    server_params = StdioServerParameters(
        command="cmd",
        args=["/c", "github-mcp-server", "stdio",
              "--toolsets", "repos,issues,users"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": token}
    )
else:  # Unix-like systems (Linux, macOS)
    server_params = StdioServerParameters(
        command="github-mcp-server",
        args=["stdio", "--toolsets", "repos,issues,users"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": token}
    )


async def setup_github(github_username: str, repository_name: str, prd_content: str, tasks: list[dict]):
    """Run the GitHub agent with the given message."""

    async with MCPTools(
            server_params=server_params,
            include_tools=["create_repository",
                           "create_or_update_file", "get_file_contents", "get_me", "create_issue"]
    ) as mcp_tools:
        tasks_string = json.dumps(tasks)

        github_setup_agent = Agent(
            model=Model,
            name="GitHub Setup Agent",
            role="Creates and configures GitHub repository with detailed README based on PRD.",
            goal="Create a new GitHub repository and generate a README.md file based on the PRD document.",
            description=(
                "Responsible for creating a new GitHub repository based on the PRD, "
                "Setting up repository configurations, and generating a comprehensive README.md file. "
                "Handles all aspects of repository initialization and README.md creation."
                "You can use all available tools to accomplish this task."
            ),
            instructions=[
                "Create a new GitHub repository according to PRD specifications (auto init false, max description length is 350 char).",
                "Generate a comprehensive README.md file (based on extracted important information based on PRD) and than update file on repository.",
                "Final Result only the GitHub repository URL without additional context"
            ],
            tools=[mcp_tools],
            reasoning=True,
            add_datetime_to_instructions=True,
            show_tool_calls=True,
            add_context=True,
            markdown=True,
            context={
                "github_username": github_username,
                "repository_name": repository_name,
                "prd_content": prd_content
            },
            debug_mode=True,
        )

        github_setup = await github_setup_agent.arun("Setup a new GitHub repository based on the PRD document provided.")

        url_pattern = r'https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+'
        repo_url = re.search(url_pattern, github_setup.content)
        repo_url = repo_url.group(
            0) if repo_url else f"https://github.com/{github_username}/{repository_name}"

        github_issue_agent = Agent(
            model=Model,
            name="GitHub Issue Agent",
            role="Creates GitHub issues based on the tasks list.",
            goal="Create GitHub issues based on the provided tasks.",
            description=(
                "Responsible for creating GitHub issues based on the provided tasks. "
                "Handles all aspects of issue creation."
                "You can use all available tools to accomplish this task."
            ),
            instructions=[
                "Create GitHub issues based on the provided tasks (use create_issue tool *MUST EXECUTE ONE by ONE*).",
                "Each task should be created as a separate issue in the GitHub repository with milestone set to 0.",
            ],
            tools=[mcp_tools],
            reasoning=True,
            add_datetime_to_instructions=True,
            show_tool_calls=True,
            markdown=True,
            add_context=True,
            debug_mode=True,
            context={
                "github_username": github_username,
                "repository_url": repo_url,
                "tasks": tasks_string,
            },
        )

        await github_issue_agent.arun(
            "Create GitHub issues based on the provided tasks."
        )

        return {
            "repository_url": repo_url,
        }


async def main():
    repository_name = f"taskflow-test-{datetime.datetime.now().strftime('%y-%m-%d-%H-%M')}"

    result = await setup_github(github_username, repository_name, prd_content, tasks)
    print(result)
    exit()

asyncio.run(main())
