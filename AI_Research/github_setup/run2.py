import json
import datetime
import os
import re
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv
from github import Github
from repo_content_generator import RepoContentGenerator, RepositoryContent

# Load environment variables 
load_dotenv()

CREDITS = "Created by TaskFlow"

async def create_or_update_readme(repo, content: str):
    """Create or update README file"""
    try:
        # Append TaskFlow credits to README
        content_with_credits = f"{content}\n\n# 🏆 Credits\n\n**{CREDITS}**"
        try:
            contents = repo.get_contents("README.md")
            repo.update_file("README.md", "Update README", content_with_credits, contents.sha)
        except:
            repo.create_file("README.md", "Add README", content_with_credits)
        print("✅ README created/updated")
    except Exception as e:
        print(f"❌ Failed to create/update README: {str(e)}")
        raise

async def create_labels(repo):
    """Create project labels"""
    labels = {
        "epic": {"color": "E53935", "description": "High-level category"},
        "feature": {"color": "1E88E5", "description": "Mid-level component"},
        "task": {"color": "43A047", "description": "Specific work item"}
    }
    
    try:
        existing_labels = {label.name: label for label in repo.get_labels()}
        for name, props in labels.items():
            if name not in existing_labels:
                repo.create_label(name=name, color=props["color"], description=props["description"])
        print("✅ Labels created")
    except Exception as e:
        print(f"❌ Failed to create labels: {str(e)}")
        raise

async def create_github_item(repo, item, item_type, milestone_map=None):
    """Generic function to create GitHub items (milestones, issues)"""
    try:
        if item_type == "milestone":
            description = f"{item['description']}\n[{CREDITS}]"
            result = repo.create_milestone(title=item["title"], description=description)
        else:
            description = f"{item['description']}\n[{CREDITS}]"
            kwargs = {
                "title": item["title"],
                "body": description,
                "labels": [item_type]
            }
            if item_type == "feature" and milestone_map:
                if milestone := milestone_map.get(item.get("parent_id")):
                    kwargs["milestone"] = milestone
            result = repo.create_issue(**kwargs)
        
        return item["id"], result
    except Exception as e:
        print(f"❌ Failed to create {item_type}: {str(e)}")
        return None

async def create_items_in_batches(repo, items, item_type, milestone_map=None, batch_size=5):
    """Generic function to create GitHub items in batches"""
    if not items:
        return {}
        
    print(f"🔨 Creating {len(items)} {item_type}s in batches...")
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    item_map = {}
    for i, batch in enumerate(batches, 1):
        print(f"📦 Processing {item_type} batch {i}/{len(batches)} ({len(batch)} items)...")
        
        # Process batch with asyncio.gather
        batch_results = await asyncio.gather(
            *(create_github_item(repo, item, item_type, milestone_map) for item in batch)
        )
        
        # Add successful results to the map
        item_map.update({id_: item for id_, item in batch_results if id_ is not None})
        
        # Add delay between batches
        if i < len(batches):
            print(f"⏳ Waiting between {item_type} batches...")
            await asyncio.sleep(1)
    
    print(f"✨ Created {len(item_map)} {item_type}s successfully")
    return item_map

async def link_task_to_feature(session, repo, github_token, parent_issue, child_issue):
    """Link a single task to its parent feature using sub-issues API"""
    url = f"https://api.github.com/repos/{repo.full_name}/issues/{parent_issue.number}/sub_issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {"sub_issue_id": child_issue.id}
    
    try:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 422:
                print(f"⚠️  Skipping link for task {child_issue.title} (might already be linked)")
                return True
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"❌ Failed to link task {child_issue.title} to feature {parent_issue.title}: {str(e)}")
        return False

async def link_tasks_to_features(repo, github_token, tasks, issue_map, batch_size=5):
    """Link tasks to features using sub-issues API with batching"""
    async with aiohttp.ClientSession() as session:
        # Filter tasks that need linking
        tasks_to_link = [
            task for task in tasks 
            if task.get("parent_id") in issue_map and task["id"] in issue_map
        ]
        
        if not tasks_to_link:
            return 0, 0
            
        print(f"🔗 Linking {len(tasks_to_link)} tasks to features in batches...")
        batches = [tasks_to_link[i:i + batch_size] for i in range(0, len(tasks_to_link), batch_size)]
        
        all_results = []
        for i, batch in enumerate(batches, 1):
            print(f"📦 Processing batch {i}/{len(batches)} ({len(batch)} tasks)...")
            
            # Process each task in the batch
            batch_results = await asyncio.gather(
                *(link_task_to_feature(
                    session, repo, github_token,
                    issue_map[task["parent_id"]],
                    issue_map[task["id"]]
                ) for task in batch)
            )
            all_results.extend(batch_results)
            
            # Add delay between batches
            if i < len(batches):
                print("⏳ Waiting between batches...")
                await asyncio.sleep(1)
        
        success = sum(1 for r in all_results if r)
        failed = len(all_results) - success
        print(f"✅ Successfully linked {success} tasks, {failed} failed")
        return success, failed

async def setup_github_project(tasks_json, github_token, prd_content=None, use_existing_repo=False, repo_url=None):
    """Set up GitHub project with repository, milestones, issues and sub-issues"""
    # Init GitHub client
    gh = Github(github_token)
    user = gh.get_user()
    
    # Process and sort tasks by type
    tasks_by_type = {
        "epic": sorted([t for t in tasks_json if t.get("task_type") == "epic"], key=lambda x: x.get("position", 999)),
        "feature": sorted([t for t in tasks_json if t.get("task_type") == "feature"], key=lambda x: x.get("position", 999)),
        "task": sorted([t for t in tasks_json if t.get("task_type") == "task"], key=lambda x: x.get("position", 999))
    }
    
    # Determine repository name
    if use_existing_repo and repo_url:
        match = re.match(r'https://github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            raise ValueError(f"Invalid repository URL: {repo_url}")
        owner, repo_name = match.groups()
        repo = gh.get_repo(f"{owner}/{repo_name}")
        print(f"📂 Using existing repository: {repo_url}")
    else:
        repo_name = f"taskflow-{datetime.datetime.now().strftime('%y-%m-%d-%H-%M')}"
    
    # Generate repository content using Agno AI
    print("🤖 Generating repository content with AI...")
    content_generator = RepoContentGenerator()
    repo_content: RepositoryContent = content_generator.generate_content(repo_name, prd_content or "No PRD provided")
    readme_content = content_generator.format_readme(repo_name, repo_content)
    
    # Create repository if not using existing one
    if not use_existing_repo:
        repo = user.create_repo(
            name=repo_name,
            description=repo_content.description,
            private=False
        )
        print(f"🎉 Created new repository: {repo.html_url}")
    
    print("\n🚀 Setting up project components in parallel...")
    
    # Phase 1: Create labels first (required for all issues)
    print("📋 Phase 1: Setting up labels...")
    await create_labels(repo)
    
    # Phase 2: Create milestones and README in parallel
    print("\n📋 Phase 2: Setting up milestones and README...")
    readme_task = create_or_update_readme(repo, readme_content)
    milestone_task = create_items_in_batches(repo, tasks_by_type["epic"], "milestone")
    
    _, milestone_map = await asyncio.gather(readme_task, milestone_task)
    
    # Phase 3: Create feature and task issues in parallel
    print("\n📋 Phase 3: Creating feature and task issues in parallel...")
    feature_task = create_items_in_batches(repo, tasks_by_type["feature"], "feature", milestone_map)
    task_task = create_items_in_batches(repo, tasks_by_type["task"], "task")
    
    feature_map, task_map = await asyncio.gather(feature_task, task_task)
    
    # Combine issue maps
    issue_map = {**feature_map, **task_map}
    
    # Phase 4: Link tasks to features
    print("\n📋 Phase 4: Linking tasks to features...")
    success, failed = await link_tasks_to_features(repo, github_token, tasks_by_type["task"], issue_map)
    
    # Build and return summary
    return {
        "url": repo.html_url,
        "name": repo.name,
        "description": repo_content.description,
        "milestones": len(milestone_map),
        "features": len(feature_map),
        "tasks": len(task_map),
        "links_successful": success,
        "links_failed": failed
    }

async def main():
    # Load data
    base_dir = Path('./test_codes/github_setup')
    with open(base_dir / 'task_hierarchy.json', 'r') as file:
        tasks_json = json.load(file)
    
    try:
        with open(base_dir / 'prd.md', 'r') as file:
            prd_content = file.read()
    except FileNotFoundError:
        prd_content = None
    
    # Get GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise RuntimeError("Please set GITHUB_TOKEN in .env file")
    
    # Run project setup
    print("🎯 Starting GitHub project setup...")
    start_time = datetime.datetime.now()
    
    result = await setup_github_project(tasks_json, github_token, prd_content)
    
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n🎉 Project setup complete in {duration:.2f} seconds!")
    print(f"📦 Repository: {result['url']}")
    print(f"📊 Created {result['milestones']} milestones, {result['features']} features, and {result['tasks']} tasks")
    print(f"🔗 Linked {result['links_successful']} tasks to features, {result['links_failed']} links failed")

if __name__ == "__main__":
    asyncio.run(main())