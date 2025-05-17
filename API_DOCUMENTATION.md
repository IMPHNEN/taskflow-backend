# TaskFlow API Documentation

## Overview

TaskFlow is a project management API that allows users to create and manage projects, generate business and product requirements documents, create tasks, and more. The API is built with FastAPI and uses Supabase for authentication and data storage.

## Base URL

All API endpoints are prefixed with `/api` as defined in the configuration.

## Authentication

The API uses JWT-based authentication with different roles:
- User
- Admin
- Super Admin

Authentication tokens must be included in the `Authorization` header using the `Bearer` scheme.

## API Endpoints

### User Routes

#### Authentication

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/api/user/auth/github/login` | GET | Get GitHub OAuth login URL | None | `{ "url": "string", "code_verifier": "string" }` |
| `/api/user/auth/github/exchange-code` | POST | Exchange GitHub OAuth code for session | `{ "code": "string", "code_verifier": "string" }` | `{ "access_token": "string", "refresh_token": "string", "expires_in": int, "user": object }` |
| `/api/user/auth/refresh` | POST | Refresh access token | `{ "refresh_token": "string" }` | `{ "access_token": "string", "refresh_token": "string", "expires_in": int }` |
| `/api/user/auth/signout` | POST | Sign out user | None | `{ "message": "Successfully signed out" }` |

#### User Info

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/api/user/me` | GET | Get current user's information | None | `{ "id": "string", "full_name": "string", "avatar_url": "string" }` |

#### Projects

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/api/user/project` | POST | Create a new project | Project data | `{ "message": "Project created successfully" }` |
| `/api/user/project` | GET | List all projects for current user | None | Array of project objects |
| `/api/user/project/{project_id}` | GET | Get a specific project with details | None | Project detail object |
| `/api/user/project/{project_id}` | PATCH | Update a project | Project update data | `{ "message": "Project updated successfully" }` |
| `/api/user/project/{project_id}` | DELETE | Delete a project | None | `{ "message": "Project deleted successfully" }` |
| `/api/user/project/{project_id}/generate-brd` | POST | Generate Business Requirements Document | None | BRD generation response |
| `/api/user/project/{project_id}/generate-prd` | POST | Generate Product Requirements Document | None | PRD generation response |
| `/api/user/project/{project_id}/generate-scope` | POST | Generate project scope (tasks) | None | Task generation response |
| `/api/user/project/{project_id}/validate-market` | POST | Validate market fit for project | None | Market validation response |
| `/api/user/project/{project_id}/setup-repository` | POST | Setup GitHub repository for project | None | Repository setup response |
| `/api/user/project/{project_id}/generate-preview` | POST | Generate project preview | None | Preview generation response |

#### Tasks

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/api/user/task/{project_id}` | POST | Create a new task | Task creation data | `{ "message": "Task created successfully" }` |
| `/api/user/task/{project_id}` | GET | List all tasks in a project | Optional: `status` query param | Array of task objects |
| `/api/user/task/{project_id}/{task_id}` | GET | Get a specific task | None | Task object |
| `/api/user/task/{project_id}/{task_id}` | PATCH | Update a task | Task update data | `{ "message": "Task updated successfully" }` |
| `/api/user/task/{project_id}/{task_id}` | DELETE | Delete a task | None | `{ "message": "Task deleted successfully" }` |
| `/api/user/task/{project_id}/reorder` | PATCH | Reorder tasks in a project | `[{ "task_id": "string", "position": int }]` | `{ "message": "Tasks reordered successfully" }` |

### Admin Routes

#### Authentication

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/api/admin/auth/login` | POST | Admin login | `username`, `password` | `{ "access_token": "string", "refresh_token": "string", "expires_in": int, "user": object }` |
| `/api/admin/auth/refresh` | POST | Refresh admin access token | `refresh_token` | `{ "access_token": "string", "refresh_token": "string", "expires_in": int }` |
| `/api/admin/auth/signout` | POST | Sign out admin | None | `{ "message": "Successfully signed out" }` |

### Super Admin Routes

#### Authentication

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/api/super/auth/login` | POST | Super admin login | `username`, `password` | `{ "access_token": "string", "refresh_token": "string", "expires_in": int, "user": object }` |
| `/api/super/auth/refresh` | POST | Refresh super admin access token | `refresh_token` | `{ "access_token": "string", "refresh_token": "string", "expires_in": int }` |
| `/api/super/auth/signout` | POST | Sign out super admin | None | `{ "message": "Successfully signed out" }` |

## Models

### Project

```python
class ProjectCreate(BaseModel):
    name: str
    description: str
    industry: str | None = None
    estimated_income: Decimal | None = None
    estimated_outcome: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
```

### Task

```python
class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    completed = "completed"

class TaskCreate(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.todo
    position: int
```

## Error Handling

All API endpoints use a common error handler that returns standardized error responses with appropriate HTTP status codes.

- 400: Bad Request - Invalid input data
- 401: Unauthorized - Missing or invalid authentication
- 403: Forbidden - Authentication valid but insufficient permissions
- 404: Not Found - Requested resource not found
- 500: Internal Server Error - Server-side error

## Background Processing

The API uses background tasks for long-running operations such as:
- BRD generation
- PRD generation
- Task generation
- Market validation

These endpoints return immediately with a status of `in_progress` and update the database when processing is complete. 