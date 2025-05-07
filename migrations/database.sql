-- Enums
CREATE TYPE user_role AS ENUM ('user', 'admin', 'super');
CREATE TYPE task_type AS ENUM ('epic', 'feature', 'task');
CREATE TYPE task_status AS ENUM ('backlog', 'todo', 'in_progress', 'done');

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
    github_access_token VARCHAR(255),
    is_banned BOOLEAN DEFAULT FALSE, --mvp belum dipake
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    objective TEXT NOT NULL,
    estimated_income DECIMAL(12,2),
    estimated_outcome DECIMAL(12,2),
    start_date DATE,
    end_date DATE,
    github_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks table (hierarchical structure)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES tasks(id), -- self-relationship for sub-tasks -- mvp belum dipake
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_type task_type NOT NULL,
    status task_status DEFAULT 'backlog',
    position INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Market Research table
CREATE TABLE market_research (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    report_markdown TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Mockups table
CREATE TABLE mockups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    preview_url VARCHAR(255),
    tool_used VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
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
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_id);
CREATE INDEX idx_activity_logs_project_id ON activity_logs(project_id);
CREATE INDEX idx_market_research_project_id ON market_research(project_id);

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


-- inserts a row into public.users
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
    insert into public.users (id, full_name, avatar_url, provider_id)
    values (new.id, new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'avatar_url', new.raw_user_meta_data ->> 'provider_id');
    return new;
end;
$$;
-- trigger the function every time a user is created
create or replace trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user();