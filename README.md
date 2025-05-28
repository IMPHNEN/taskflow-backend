# TaskFlow Backend

TaskFlow is a project management API that helps users manage projects, tasks, and generate project documentation using AI.

## Features

- User, Admin, and Super Admin authentication
- Project management
- Task management
- AI-powered document generation (BRD, PRD)
- GitHub repository integration
- Market validation
- Project preview generation

## API Documentation

For detailed API documentation, please see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md).

## Setup

### Standard Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run the application: `python run.py`

### Docker Setup

1. Clone the repository
2. Create a `.env` file based on `.env.example`
3. Build the Docker image:
   ```bash
   docker build -t taskflow-backend .
   ```
4. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env taskflow-backend
   ```

## Environment Variables

See `.env.example` for a complete list of required and optional environment variables. Key variables include:

- Supabase credentials for authentication and database
- Frontend URL for CORS configuration
- AI service API keys (OpenAI, Groq, Google, Mistral)
- Model configurations for different AI features
- GitHub integration settings

## Backend Structure

- `app/` - Main application code
  - `routes/` - API route definitions
  - `models/` - Data models
  - `services/` - Business logic services
  - `middleware/` - Request middleware
  - `utils/` - Utility functions
  - `config.py` - Application configuration
  - `main.py` - Application entry point
