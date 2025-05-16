-- Drop triggers first
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP TRIGGER IF EXISTS update_projects_modtime ON projects;
DROP TRIGGER IF EXISTS update_tasks_modtime ON tasks;
DROP TRIGGER IF EXISTS update_market_research_modtime ON market_research;

-- Drop functions
DROP FUNCTION IF EXISTS public.handle_new_user();
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables in correct order (respecting foreign key constraints)
DROP TABLE IF EXISTS activity_logs;
DROP TABLE IF EXISTS mockup;
DROP TABLE IF EXISTS prd;
DROP TABLE IF EXISTS github_setup;
DROP TABLE IF EXISTS market_research;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

-- Drop types
DROP TYPE IF EXISTS user_role;
DROP TYPE IF EXISTS task_type;
DROP TYPE IF EXISTS task_status;
DROP TYPE IF EXISTS ai_generation_status;
-- Drop extensions (optional, comment out if you want to keep them)
-- DROP EXTENSION IF EXISTS "uuid-ossp";
-- DROP EXTENSION IF EXISTS vector; 