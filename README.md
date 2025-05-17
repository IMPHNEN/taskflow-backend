# TaskFlow Backend

TaskFlow is a project management API that helps users manage projects, tasks, and generate project documentation using AI.

## Features

- User, Admin, and Super Admin authentication
- Project management
- Task management
- AI-powered document generation (BRD, PRD)
- GitHub repository integration
- Market validation

## API Documentation

For detailed API documentation, please see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md).

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run the application: `python run.py`

## Backend Structure

- `app/` - Main application code
  - `routes/` - API route definitions
  - `models/` - Data models
  - `services/` - Business logic services
  - `middleware/` - Request middleware
  - `utils/` - Utility functions
  - `config.py` - Application configuration
  - `main.py` - Application entry point