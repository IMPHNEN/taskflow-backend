-- Enums
CREATE TYPE user_role AS ENUM ('user', 'admin', 'super');
CREATE TYPE task_type AS ENUM ('epic', 'feature', 'task');
CREATE TYPE task_status AS ENUM ('backlog', 'todo', 'in_progress', 'done');
CREATE TYPE ai_generation_status AS ENUM ('not_started','in_progress', 'completed', 'failed');

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table
CREATE TABLE public.users (
    id UUID PRIMARY KEY NOT NULL REFERENCES auth.users ON DELETE CASCADE,
    full_name TEXT,
    avatar_url TEXT,
    role user_role DEFAULT 'user', --mvp belum dipake
    provider_id VARCHAR(50) UNIQUE,
    provider_username VARCHAR(50) UNIQUE,
    github_access_token VARCHAR(255),
    is_banned BOOLEAN DEFAULT FALSE, --mvp belum dipake
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) NOT NULL ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    objective TEXT NOT NULL,
    estimated_income DECIMAL(12,2) NOT NULL,
    estimated_outcome DECIMAL(12,2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks table (hierarchical structure)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL ON DELETE CASCADE,
    parent_id UUID REFERENCES tasks(id), -- self-relationship for sub-tasks -- mvp belum dipake
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_type task_type NOT NULL,
    status task_status DEFAULT 'backlog',
    position INTEGER NOT NULL,
    story_point INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- BRD table
CREATE TABLE brd (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL ON DELETE CASCADE UNIQUE,
    brd_markdown TEXT,
    status ai_generation_status DEFAULT 'not_started',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- PRD table
CREATE TABLE prd (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL ON DELETE CASCADE UNIQUE,
    prd_markdown TEXT,
    status ai_generation_status DEFAULT 'not_started',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Github Setup table
CREATE TABLE github_setup (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL ON DELETE CASCADE UNIQUE,
    repository_url VARCHAR(255),
    status ai_generation_status DEFAULT 'not_started',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Market Research table
CREATE TABLE market_research (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL ON DELETE CASCADE UNIQUE,
    report_markdown TEXT,
    status ai_generation_status DEFAULT 'not_started',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Mockup table
CREATE TABLE mockup (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL ON DELETE CASCADE UNIQUE,
    preview_url VARCHAR(255),
    tool_used VARCHAR(50),
    status ai_generation_status DEFAULT 'not_started',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activity Logs table
-- Optional, mvp belum dipake :v
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_activity_logs_project_id ON activity_logs(project_id);
CREATE INDEX idx_market_research_project_id ON market_research(project_id);
-- Add tasks indexes for better performance
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_id);
CREATE INDEX idx_tasks_project_parent_pos ON tasks(project_id, parent_id, position);
CREATE INDEX idx_tasks_parent_pos ON tasks(parent_id, position);
CREATE INDEX idx_tasks_proj_parent_pos ON tasks(project_id, COALESCE(parent_id, uuid_nil()), position);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Update timestamp triggers
CREATE OR REPLACE TRIGGER update_projects_modtime
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_tasks_modtime
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_market_research_modtime
    BEFORE UPDATE ON market_research
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_mockup_modtime
    BEFORE UPDATE ON mockup
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_prd_modtime
    BEFORE UPDATE ON prd
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE OR REPLACE TRIGGER update_github_setup_modtime
    BEFORE UPDATE ON github_setup
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();


-- Optimized function to adjust task positions
CREATE OR REPLACE FUNCTION adjust_task_positions()
RETURNS TRIGGER AS $$
DECLARE
    max_position INTEGER;
    parent_key   UUID := COALESCE(NEW.parent_id, uuid_nil());
BEGIN
    -- Prevent recursive trigger loops
    IF pg_trigger_depth() > 1 THEN
        RETURN NEW;
    END IF;

    -- Find current max position among siblings
    SELECT COALESCE(MAX(position), 0)
        INTO max_position
        FROM tasks
        WHERE project_id = NEW.project_id
        AND COALESCE(parent_id, uuid_nil()) = parent_key;

    -- Assign or shift
    IF NEW.position IS NULL 
        OR NEW.position > max_position + 1 THEN
        NEW.position := max_position + 1;
    ELSE
        NEW.position := GREATEST(1, NEW.position);
        UPDATE tasks
            SET position = position + 1
            WHERE project_id = NEW.project_id
            AND COALESCE(parent_id, uuid_nil()) = parent_key
            AND position >= NEW.position;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Function: handle_task_position_update()
CREATE OR REPLACE FUNCTION handle_task_position_update()
RETURNS TRIGGER AS $$
DECLARE
    old_pos       INTEGER := OLD.position;
    new_pos       INTEGER;
    max_position  INTEGER;
    old_parent    UUID := COALESCE(OLD.parent_id, uuid_nil());
    new_parent    UUID := COALESCE(NEW.parent_id, uuid_nil());
BEGIN
    -- Prevent recursive trigger loops
    IF pg_trigger_depth() > 1 THEN
        RETURN NEW;
    END IF;

    -- No-op if nothing meaningful changed
    IF old_pos = NEW.position
        AND old_parent = new_parent THEN
        RETURN NEW;
    END IF;

    -- Bound new_pos into [1..max+1]
    SELECT COALESCE(MAX(position), 0)
        INTO max_position
        FROM tasks
        WHERE project_id = NEW.project_id
        AND COALESCE(parent_id, uuid_nil()) = new_parent
        AND id <> NEW.id;

    new_pos := LEAST(GREATEST(1, NEW.position), max_position + 1);

    IF old_parent = new_parent THEN
        -- Reordering within same bucket
        IF new_pos > old_pos THEN
            UPDATE tasks
                SET position = position - 1
                WHERE project_id = NEW.project_id
                AND COALESCE(parent_id, uuid_nil()) = new_parent
                AND position > old_pos
                AND position <= new_pos
                AND id <> NEW.id;
        ELSE
            UPDATE tasks
                SET position = position + 1
                WHERE project_id = NEW.project_id
                AND COALESCE(parent_id, uuid_nil()) = new_parent
                AND position >= new_pos
                AND position < old_pos
                AND id <> NEW.id;
        END IF;
    ELSE
        -- Moving between buckets: close old gap…
        UPDATE tasks
            SET position = position - 1
            WHERE project_id = NEW.project_id
            AND COALESCE(parent_id, uuid_nil()) = old_parent
            AND position > old_pos;

        -- …and open new slot
        UPDATE tasks
            SET position = position + 1
            WHERE project_id = NEW.project_id
            AND COALESCE(parent_id, uuid_nil()) = new_parent
            AND position >= new_pos
            AND id <> NEW.id;
    END IF;

    NEW.position := new_pos;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- triggers before_task_insert, before_task_position_update
CREATE OR REPLACE TRIGGER before_task_insert
    BEFORE INSERT ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION adjust_task_positions();

CREATE OR REPLACE TRIGGER before_task_position_update
    BEFORE UPDATE OF position, parent_id ON tasks
    FOR EACH ROW
    WHEN (
        (OLD.position IS DISTINCT FROM NEW.position)
        OR (OLD.parent_id IS DISTINCT FROM NEW.parent_id)
    )
    EXECUTE FUNCTION handle_task_position_update();

-- inserts a row into public.users
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
    insert into public.users (id, full_name, avatar_url, provider_id, provider_username)
    values (new.id, new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'avatar_url', new.raw_user_meta_data ->> 'provider_id', new.raw_user_meta_data ->> 'provider_username');
    return new;
end;
$$;
-- trigger the function every time a user is created
create or replace trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user();