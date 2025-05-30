-- Drop triggers first
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP TRIGGER IF EXISTS update_projects_modtime ON projects;
DROP TRIGGER IF EXISTS update_tasks_modtime ON tasks;
DROP TRIGGER IF EXISTS update_market_research_modtime ON market_research;
DROP TRIGGER IF EXISTS update_mockup_modtime ON mockup;
DROP TRIGGER IF EXISTS update_prd_modtime ON prd;
DROP TRIGGER IF EXISTS update_github_setup_modtime ON github_setup;
DROP TRIGGER IF EXISTS update_feedback_modtime ON feedback;
DROP TRIGGER IF EXISTS before_task_insert ON tasks;
DROP TRIGGER IF EXISTS before_task_position_update ON tasks;

-- Drop functions
DROP FUNCTION IF EXISTS public.handle_new_user();
DROP FUNCTION IF EXISTS update_updated_at_column();
DROP FUNCTION IF EXISTS adjust_task_positions();
DROP FUNCTION IF EXISTS handle_task_position_update();
DROP FUNCTION IF EXISTS update_feedback_modtime();

-- Drop tables in correct order (respecting foreign key constraints)
DROP TABLE IF EXISTS activity_logs;
DROP TABLE IF EXISTS mockup;
DROP TABLE IF EXISTS prd;
DROP TABLE IF EXISTS brd;
DROP TABLE IF EXISTS github_setup;
DROP TABLE IF EXISTS market_research;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS ai.agent_sessions;
DROP TABLE IF EXISTS ai.user_memories;

-- Drop types
DROP TYPE IF EXISTS user_role;
DROP TYPE IF EXISTS task_type;
DROP TYPE IF EXISTS task_status;
DROP TYPE IF EXISTS ai_generation_status;
-- Drop extensions (optional, comment out if you want to keep them)
-- DROP EXTENSION IF EXISTS "uuid-ossp";
-- DROP EXTENSION IF EXISTS vector; 