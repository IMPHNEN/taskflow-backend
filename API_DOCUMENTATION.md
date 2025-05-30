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

| Endpoint                              | Method | Description                            | Parameters                                        | Response                                                                                     |
| ------------------------------------- | ------ | -------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `/api/user/auth/github/login`         | GET    | Get GitHub OAuth login URL             | None                                              | `{ "url": "string", "code_verifier": "string" }`                                             |
| `/api/user/auth/github/exchange-code` | POST   | Exchange GitHub OAuth code for session | `{ "code": "string", "code_verifier": "string" }` | `{ "access_token": "string", "refresh_token": "string", "expires_in": int, "user": object }` |
| `/api/user/auth/refresh`              | POST   | Refresh access token                   | `{ "refresh_token": "string" }`                   | `{ "access_token": "string", "refresh_token": "string", "expires_in": int }`                 |
| `/api/user/auth/signout`              | POST   | Sign out user                          | `{ "refresh_token": "string" }`                   | `{ "message": "Successfully signed out" }`                                                   |

#### User Info

| Endpoint       | Method | Description                    | Parameters | Response                                                            |
| -------------- | ------ | ------------------------------ | ---------- | ------------------------------------------------------------------- |
| `/api/user/me` | GET    | Get current user's information | None       | `{ "id": "string", "full_name": "string", "avatar_url": "string" }` |

#### GitHub Integration

| Endpoint                           | Method | Description               | Parameters                                        | Response                                         |
| ---------------------------------- | ------ | ------------------------- | ------------------------------------------------- | ------------------------------------------------ |
| `/api/user/setting/github/connect` | GET    | Get GitHub connection URL | None                                              | `{ "url": "string", "code_verifier": "string" }` |
| `/api/user/setting/github/verify`  | POST   | Verify GitHub connection  | `{ "code": "string", "code_verifier": "string" }` | `{ "message": "GitHub successfully connected" }` |

#### Projects

| Endpoint                                          | Method | Description                             | Parameters                                                                                                                                                   | Response                                        |
| ------------------------------------------------- | ------ | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- |
| `/api/user/project`                               | POST   | Create a new project                    | `{ "name": "string", "objective": "string", "estimated_income": number, "estimated_outcome": number, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }` | `{ "message": "Project created successfully" }` |
| `/api/user/project`                               | GET    | List all projects for current user      | None                                                                                                                                                         | Array of project objects                        |
| `/api/user/project/{project_id}`                  | GET    | Get a specific project with details     | None                                                                                                                                                         | Project detail object                           |
| `/api/user/project/{project_id}`                  | PATCH  | Update a project                        | Project update data                                                                                                                                          | `{ "message": "Project updated successfully" }` |
| `/api/user/project/{project_id}`                  | DELETE | Delete a project                        | None                                                                                                                                                         | `{ "message": "Project deleted successfully" }` |
| `/api/user/project/{project_id}/generate-brd`     | POST   | Generate Business Requirements Document | None                                                                                                                                                         | BRD generation response                         |
| `/api/user/project/{project_id}/generate-prd`     | POST   | Generate Product Requirements Document  | None                                                                                                                                                         | PRD generation response                         |
| `/api/user/project/{project_id}/generate-scope`   | POST   | Generate project scope (tasks)          | None                                                                                                                                                         | Task generation response                        |
| `/api/user/project/{project_id}/validate-market`  | POST   | Validate market fit for project         | None                                                                                                                                                         | Market validation response                      |
| `/api/user/project/{project_id}/setup-repository` | POST   | Setup GitHub repository for project     | None                                                                                                                                                         | Repository setup response                       |
| `/api/user/project/{project_id}/generate-preview` | POST   | Generate project preview                | None                                                                                                                                                         | Preview generation response                     |

#### Tasks

| Endpoint                                | Method | Description                 | Parameters                                                                                                    | Response                                     |
| --------------------------------------- | ------ | --------------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `/api/user/task/{project_id}`           | POST   | Create a new task           | `{ "title": "string", "task_type": "string", "status": "string", "story_point": number, "position": number }` | `{ "message": "Task created successfully" }` |
| `/api/user/task/{project_id}`           | GET    | List all tasks in a project | None                                                                                                          | Array of task objects                        |
| `/api/user/task/{project_id}/{task_id}` | GET    | Get a specific task         | None                                                                                                          | Task object                                  |
| `/api/user/task/{project_id}/{task_id}` | PATCH  | Update a task               | Task update data                                                                                              | `{ "message": "Task updated successfully" }` |
| `/api/user/task/{project_id}/{task_id}` | DELETE | Delete a task               | None                                                                                                          | `{ "message": "Task deleted successfully" }` |
| `/api/user/task/{project_id}/reorder`   | PATCH  | Reorder tasks in a project  | `[{ "task_id": "string", "position": int }]`                                              | `{ "message": "Tasks reordered successfully" }` |

#### Feedback

| Endpoint                | Method | Description         | Parameters                                               | Response                                          |
| ----------------------- | ------ | ------------------- | -------------------------------------------------------- | ------------------------------------------------- |
| `/api/user/feedback`    | POST   | Submit new feedback | `{ "title": "string", "content": "string", "rating": int }` | `{ "message": "Feedback submitted successfully" }` |

## Models

### Project

```python
class ProjectCreate(BaseModel):
    name: str
    objective: str
    industry: str | None = None
    estimated_income: Decimal | None = None
    estimated_outcome: Decimal | None = None
    start_date: date | None = None
    end_date: date | None = None
```

### Task

```python
class TaskType(str, Enum):
    epic = "epic"
    story = "story"
    task = "task"

class TaskStatus(str, Enum):
    backlog = "backlog"
    todo = "todo"
    in_progress = "in_progress"
    completed = "completed"

class TaskCreate(BaseModel):
    title: str
    description?: str
    task_type: TaskType
    task_status: TaskStatus
    position: int
```

### Feedback

```python
class FeedbackCreate(BaseModel):
    title: str
    content: str
    rating: int  # 1-5 rating
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
- Repository setup
- Project preview generation

These endpoints return immediately with a status of `in_progress` and update the database when processing is complete.
