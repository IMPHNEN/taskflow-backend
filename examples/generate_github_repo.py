"""
Example script to test GitHub repository setup.
"""
import os
import sys
import json
import asyncio
import uuid
from dotenv import load_dotenv

# Add the project root directory to the Python path if running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.github_setup import GitHubSetupService

# Load environment variables
load_dotenv()

async def main():
    # Load sample data
    with open('examples/data/sample_tasks.json', 'r') as f:
        tasks_json = json.load(f)
    
    with open('examples/data/sample_prd.md', 'r') as f:
        prd_content = f.read()
    
    # Get GitHub token from terminal input
    print("\n🔑 GitHub Token Setup")
    print("You can create a token at: https://github.com/settings/tokens")
    print("Required scopes: repo, admin:repo_hook, read:user, user:email")
    github_token = input("Enter your GitHub token: ").strip()
    
    if not github_token:
        raise RuntimeError("GitHub token is required")
    
    print("\n🚀 Starting GitHub repository setup...")
    
    try:
        # Initialize the GitHub setup service
        github_service = GitHubSetupService()
        
        # Random UUID
        project_id = "28cf12ac-2f5e-4dd5-99b6-26a889f42a45"
        # project_id = str(uuid4())
        
        # Create project details
        project_details = {
            "name": "Sample Project",
            "tasks_generated": tasks_json
        }
        
        # Run the setup
        result = await github_service.setup_repository(
            project_details=project_details,
            prd_content=prd_content,
            github_token=github_token,
            project_id=project_id
        )
        
        if result["status"] == "success":
            print("\n✅ Repository setup completed!")
            print(f"📦 Repository URL: {result['repository_url']}")
            print(f"📊 Statistics:")
            print(f"   - Milestones: {result['stats']['milestones']}")
            print(f"   - Features: {result['stats']['features']}")
            print(f"   - Tasks: {result['stats']['tasks']}")
            print(f"   - Successful links: {result['stats']['links_successful']}")
            print(f"   - Failed links: {result['stats']['links_failed']}")
        else:
            print(f"\n❌ Repository setup failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"\n❌ Repository setup failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 