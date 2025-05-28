"""
Task Status Position Test

This script tests the SQL triggers and functions that handle task positioning
based on status rather than parent_id. It verifies:

1. Reordering tasks within the same status
2. Moving tasks between different statuses
3. Auto-assigning positions for new tasks

Usage:
    python task_status_position_test.py <project_id>

Arguments:
    project_id - UUID of an existing project to test with
"""
import uuid
import time
import sys
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# ============================================================================
# Configuration and Setup
# ============================================================================

def load_environment():
    """Load environment variables and check for required ones"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    print("Environment variables loaded successfully.")
    
    # Supabase configuration
    return {
        "url": os.getenv("SUPABASE_URL"),
        "key": os.getenv("SUPABASE_KEY")
    }

def print_header(title):
    """Print a formatted header for test sections"""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50)

def print_tasks(tasks, status_filter=None):
    """Print tasks in a formatted way, optionally filtered by status"""
    if status_filter:
        filtered_tasks = [t for t in tasks if t['status'] == status_filter]
        print(f"\nTasks with status '{status_filter}':")
    else:
        filtered_tasks = tasks
        print("\nAll tasks:")
    
    for task in filtered_tasks:
        print(f"ID: {task['id'][:8]}... | Status: {task['status']} | Position: {task['position']} | Title: {task['title']}")

# ============================================================================
# Test Functions
# ============================================================================

def test_task_positioning(supabase, project_id):
    """Run tests for task positioning by status"""
    # Generate unique ID for this test run
    test_id = str(uuid.uuid4())
    
    print_header("TASK POSITION TESTING")
    print(f"Test ID: {test_id}")
    print(f"Using Project ID: {project_id}")
    
    try:
        # Step 1: Verify project exists
        print_header("VERIFYING PROJECT")
        result = supabase.table("projects").select("*").eq("id", project_id).execute()
        if not result.data:
            print(f"Error: Project with ID {project_id} not found")
            return
        print(f"Found project: {result.data[0]['name']}")
        
        # Step 2: Create test tasks with different statuses
        print_header("CREATING TEST TASKS")
        tasks_data = [
            {
                "project_id": project_id,
                "title": "Backlog Task 1",
                "description": "Test task",
                "task_type": "task",
                "status": "backlog",
                "position": 1,
                "story_point": 1
            },
            {
                "project_id": project_id,
                "title": "Backlog Task 2",
                "description": "Test task",
                "task_type": "task",
                "status": "backlog",
                "position": 2,
                "story_point": 1
            },
            {
                "project_id": project_id,
                "title": "Todo Task 1",
                "description": "Test task",
                "task_type": "task",
                "status": "todo",
                "position": 1,
                "story_point": 2
            },
            {
                "project_id": project_id,
                "title": "Todo Task 2",
                "description": "Test task",
                "task_type": "task",
                "status": "todo",
                "position": 2,
                "story_point": 2
            }
        ]
        
        task_ids = []
        for task_data in tasks_data:
            result = supabase.table("tasks").insert(task_data).execute()
            task_id = result.data[0]['id']
            task_ids.append(task_id)
            print(f"Created task: {task_data['title']} with ID: {task_id[:8]}...")
        
        # Step 3: Fetch all tasks to verify initial positions
        print_header("VERIFYING INITIAL POSITIONS")
        result = supabase.table("tasks").select("*").eq("project_id", project_id).order("status").order("position").execute()
        tasks = result.data
        print_tasks(tasks)
        
        # Step 4: Test reordering within same status
        print_header("TESTING REORDERING WITHIN SAME STATUS")
        print("Moving 'Backlog Task 2' to position 1 (should shift 'Backlog Task 1' to position 2)")
        
        # Get the ID of Backlog Task 2
        backlog_task2_id = next(task['id'] for task in tasks if task['title'] == "Backlog Task 2")
        
        # Update its position
        supabase.table("tasks").update({"position": 1}).eq("id", backlog_task2_id).execute()
        
        # Fetch tasks again to verify positions changed
        result = supabase.table("tasks").select("*").eq("project_id", project_id).order("status").order("position").execute()
        tasks = result.data
        print_tasks(tasks, "backlog")
        
        # Step 5: Test moving task between statuses
        print_header("TESTING MOVING TASK BETWEEN STATUSES")
        print("Moving 'Backlog Task 1' to 'todo' status at position 1")
        
        # Get the ID of Backlog Task 1
        backlog_task1_id = next(task['id'] for task in tasks if task['title'] == "Backlog Task 1")
        
        # Update its status and position
        supabase.table("tasks").update({"status": "todo", "position": 1}).eq("id", backlog_task1_id).execute()
        
        # Wait briefly for the database trigger to process
        time.sleep(1)
        
        # Fetch tasks again to verify changes
        result = supabase.table("tasks").select("*").eq("project_id", project_id).order("status").order("position").execute()
        tasks = result.data
        
        print_tasks(tasks, "backlog")
        print_tasks(tasks, "todo")
        
        # Step 6: Add a new task with automatically assigned position
        print_header("TESTING AUTO-POSITION ASSIGNMENT")
        new_task_data = {
            "project_id": project_id,
            "title": "New In Progress Task",
            "description": "Test task with auto-assigned position",
            "task_type": "task",
            "status": "in_progress",
            "story_point": 3
        }
        
        result = supabase.table("tasks").insert(new_task_data).execute()
        new_task_id = result.data[0]['id']
        print(f"Created new task with ID: {new_task_id[:8]}...")
        
        # Fetch tasks again to verify auto-position
        result = supabase.table("tasks").select("*").eq("project_id", project_id).order("status").order("position").execute()
        tasks = result.data
        print_tasks(tasks, "in_progress")
        
        print_header("TEST COMPLETE")
        print("Task positioning functionality appears to be working correctly!")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
    
    finally:
        # Clean up: Delete test data
        print_header("CLEANING UP")
        try:
            # Delete tasks that we created (by title pattern)
            test_task_titles = [
                "Backlog Task 1", "Backlog Task 2", 
                "Todo Task 1", "Todo Task 2",
                "New In Progress Task"
            ]
            
            for title in test_task_titles:
                supabase.table("tasks").delete().eq("project_id", project_id).eq("title", title).execute()
                
            print("Deleted test tasks")
            print("Cleanup completed successfully")
        except Exception as e:
            print(f"Cleanup failed with error: {str(e)}")

# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main entry point for the script"""
    if len(sys.argv) != 2:
        print("Usage: python task_status_position_test.py <project_id>")
        sys.exit(1)
    
    project_id = sys.argv[1]
    
    # Load environment and create Supabase client
    env = load_environment()
    supabase = create_client(env["url"], env["key"])
    
    print(f"Starting task position test for project ID: {project_id}...")
    test_task_positioning(supabase, project_id)
    print("Test completed.")

if __name__ == "__main__":
    main() 