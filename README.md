# TaskFlow Backend

**An AI-Driven Project Management Platform for Solo Entrepreneurs and Small Teams**

TaskFlow is a comprehensive project management API that leverages artificial intelligence to streamline project planning, execution, and validation. The platform automates complex workflows including project scope generation, repository setup, visual mockup creation, market validation, and advanced analytics - empowering users to transform ideas into successful projects with unprecedented efficiency.

---

## 🚀 Project Purpose

TaskFlow addresses the challenges faced by solo entrepreneurs and small teams in managing complex projects by providing:

- **Intelligent Project Planning**: AI-powered generation of Business Requirements Documents (BRD) and Product Requirements Documents (PRD)
- **Automated Repository Management**: Seamless GitHub integration with automated issue creation and milestone tracking
- **Market Intelligence**: Multi-agent market validation system with competitor analysis and opportunity assessment
- **Visual Prototyping**: Automated mockup generation using Lovable AI for rapid visualization
- **Smart Task Management**: AI-driven task breakdown and prioritization
- **Advanced Analytics**: Comprehensive project insights and performance metrics

---

## 🤖 AI Features Overview

### Core AI Services

| Service | Purpose | AI Models Supported | Key Features |
|---------|---------|-------------------|--------------|
| **BRD Generator** | Business Requirements Documents | OpenAI, Groq, Gemini, Mistral | Automated business analysis, stakeholder identification, requirement extraction |
| **PRD Generator** | Product Requirements Documents | OpenAI, Groq, Gemini, Mistral | Feature specification, technical requirements, user story generation |
| **Task Generator** | Intelligent Task Creation | OpenAI, Groq, Gemini, Mistral | Task breakdown, dependency mapping, effort estimation |
| **Market Validation** | Multi-Agent Market Analysis | OpenAI, Gemini, Groq | Competitor research, market sizing, opportunity analysis |
| **GitHub Setup** | Repository Automation | OpenAI, Groq, Gemini, Mistral | Automated repo creation, issue generation, milestone planning |
| **Preview Generator** | Visual Mockup Creation | Lovable AI via OpenRouter | Website mockups, UI prototyping, design automation |

### AI Agent Architecture

- **Multi-Model Support**: Flexible AI provider configuration (OpenAI, Groq, Google Gemini, Mistral)
- **Memory Management**: Persistent context storage using Mem0ai for enhanced AI interactions
- **Multi-Agent Teams**: Specialized agents for market research, analysis, and reporting
- **Tool Integration**: Tavily for web research, Firecrawl for content extraction, GitHub API for automation

---

## 📋 Prerequisites & Configuration

### System Requirements

- **Python**: 3.11 or higher
- **Database**: PostgreSQL (via Supabase)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB available space

### Required API Keys

| Service | Required For | How to Obtain |
|---------|-------------|---------------|
| **Supabase** | Database & Authentication | [supabase.com](https://supabase.com) |
| **OpenAI** | GPT models | [platform.openai.com](https://platform.openai.com) |
| **Groq** | Fast inference models | [console.groq.com](https://console.groq.com) |
| **Google AI** | Gemini models | [ai.google.dev](https://ai.google.dev) |
| **Mistral** | Mistral models | [console.mistral.ai](https://console.mistral.ai) |
| **OpenRouter** | Preview generation | [openrouter.ai](https://openrouter.ai) |
| **Tavily** | Market research | [tavily.com](https://tavily.com) |
| **Firecrawl** | Content extraction | [firecrawl.dev](https://firecrawl.dev) |
| **Lovable** | UI mockup generation | Contact Lovable for access |

---

## 🛠️ Installation & Development Workflow

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/taskflow-backend.git
cd taskflow-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Run the application
python run.py
```

### Docker Setup

```bash
# Build the Docker image
docker build -t taskflow-backend .

# Run with environment file
docker run -p 8000:8000 --env-file .env taskflow-backend

# Or run with docker-compose (if available)
docker-compose up --build
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pre-commit install

# Run in development mode
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Access the API documentation
# http://localhost:8000/api/docs (Swagger UI)
# http://localhost:8000/api/redoc (ReDoc)
```

### Environment Configuration

Create a `.env` file based on `.env.example`:

```bash
# Core Services
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
FRONTEND_URL=http://localhost:3000

# AI Model Configuration
DEFAULT_MODEL_TYPE=groq
DEFAULT_MODEL_ID=llama-3.3-70b-versatile

# API Keys
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
MISTRAL_API_KEY=your_mistral_key
OPENROUTER_API_KEY=your_openrouter_key
TAVILY_API_KEY=your_tavily_key
FIRECRAWL_API_KEY=your_firecrawl_key

# Service Settings
ENABLE_DEBUG_MODE=False
ENABLE_MARKDOWN=True
RESULTS_DIR=results
```

---

## 📁 Detailed Folder Structure

```
taskflow-backend/
├── 📄 API_DOCUMENTATION.md         # Comprehensive API reference
├── 🐳 Dockerfile                   # Container configuration
├── 📄 requirements.txt             # Python dependencies
├── 🚀 run.py                       # Application entry point
├── ⚙️ pyproject.toml               # Project configuration
└── 📦 app/                         # Main application code
    ├── 🎯 main.py                  # FastAPI application setup
    ├── ⚙️ config.py                # Configuration and service initialization
    ├── 🔒 middleware/              # Authentication and request middleware
    │   └── auth.py                 # JWT authentication logic
    ├── 📊 models/                  # Pydantic data models
    │   ├── user.py                 # User and authentication models
    │   ├── project.py              # Project management models
    │   ├── task.py                 # Task and workflow models
    │   ├── brd.py                  # Business Requirements models
    │   ├── prd.py                  # Product Requirements models
    │   ├── market_research.py      # Market validation models
    │   ├── github_setup.py         # Repository automation models
    │   └── mockup.py               # Preview generation models
    ├── 🛣️ routes/                  # API endpoint definitions
    │   ├── user/                   # User-facing endpoints
    │   │   ├── auth.py             # Authentication endpoints
    │   │   ├── project.py          # Project management API
    │   │   ├── task.py             # Task management API
    │   │   ├── setting.py          # User preferences API
    │   │   └── index.py            # User information API
    │   ├── admin/                  # Admin panel endpoints
    │   │   └── auth.py             # Admin authentication
    │   └── super/                  # Super admin endpoints
    │       └── auth.py             # Super admin authentication
    ├── 🧠 services/                # AI-powered business logic
    │   ├── config.py               # AI model configurations
    │   ├── models.py               # AI model factory and utilities
    │   ├── memory_storage_service.py # Memory management for AI agents
    │   ├── brd_generator.py        # Business Requirements AI service
    │   ├── prd_generator.py        # Product Requirements AI service
    │   ├── task_generator.py       # Intelligent task creation
    │   ├── market_validation.py    # Multi-agent market analysis
    │   ├── github_setup.py         # Repository automation service
    │   ├── preview_generator.py    # Visual mockup generation
    │   ├── templates/              # AI prompt templates
    │   └── toolkits/               # Custom AI tools and integrations
    └── 🔧 utils/                   # Utility functions
        ├── ai_utils.py             # AI helper functions
        ├── background_tasks.py     # Asynchronous task processing
        ├── error_handler.py        # Error handling utilities
        └── github_utils.py         # GitHub API utilities

├── 📚 examples/                    # Usage examples and demos
│   ├── generate_brd.py             # BRD generation example
│   ├── generate_prd.py             # PRD generation example
│   ├── generate_tasks.py           # Task generation example
│   ├── run_market_validation.py    # Market validation example
│   ├── generate_github_repo.py     # GitHub automation example
│   ├── generate_preview.py         # Mockup generation example
│   ├── document_generation_flow.py # Complete workflow example
│   └── data/                       # Sample data and outputs
│       ├── sample_brd.md
│       ├── sample_prd.md
│       └── sample_tasks.json

├── 🔧 github_setup/               # GitHub automation tools
│   ├── repo_content_generator.py   # Repository content automation
│   ├── build-github-mcp.txt        # GitHub MCP configuration
│   └── task_hierarchy.json         # Task structure templates

├── 📊 market_validation/           # Market research tools
│   ├── mv.ipynb                    # Market validation notebook
│   └── taskflow_market_validation.py # Standalone validation script

├── 🗄️ migrations/                 # Database schema and setup
│   ├── database.sql                # Database schema
│   └── clean_database.sql          # Database cleanup scripts

├── 📄 prd_generation/              # Document generation tools
│   ├── brd_generation.py           # BRD generation utilities
│   ├── task_generator_pydantic.py  # Task generation models
│   └── README.md                   # PRD generation documentation

└── 📈 results/                     # Generated outputs and reports
    └── market_validation_report_*.md # Market validation reports
```

---

## 🎯 Usage Examples

### 1. Generate Business Requirements Document

```python
from app.services.brd_generator import BRDGeneratorService

# Initialize the service
brd_service = BRDGeneratorService()

# Generate BRD
project_description = "A mobile app for food delivery with real-time tracking"
result = await brd_service.generate_brd(project_description, "project-123")

print(result["brd_content"])  # Generated BRD in markdown format
```

### 2. Run Market Validation

```python
from app.services.market_validation import MarketValidationService

# Initialize the multi-agent market validation service
market_service = MarketValidationService()

# Run comprehensive market analysis
project_description = "AI-powered fitness coaching app"
result = await market_service.run_market_validation(project_description, "project-456")

print(f"Market Size: {result['market_analysis']['market_size']}")
print(f"Competition Level: {result['market_analysis']['competition_level']}")
```

### 3. Automate GitHub Repository Setup

```python
from app.services.github_setup import GitHubSetupService

# Initialize GitHub automation service
github_service = GitHubSetupService()

# Create repository with automated issues and milestones
project_data = {
    "name": "TaskFlow Mobile App",
    "description": "Mobile project management application",
    "tech_stack": ["React Native", "Node.js", "PostgreSQL"]
}

result = await github_service.setup_github_repository(project_data, "project-789")
print(f"Repository created: {result['repository_url']}")
```

### 4. Generate Visual Mockups

```python
from app.services.preview_generator import PreviewGeneratorService

# Initialize preview generation service
preview_service = PreviewGeneratorService()

# Generate website mockup
project_description = "E-commerce platform for handmade crafts"
result = await preview_service.generate_preview(project_description, "project-101")

print(f"Preview URL: {result['preview_url']}")
print(f"Generated Files: {result['generated_files']}")
```

### 5. API Usage Examples

#### Authentication
```bash
# Register a new user
curl -X POST "http://localhost:8000/api/user/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure123"}'

# Login
curl -X POST "http://localhost:8000/api/user/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure123"}'
```

#### Project Management
```bash
# Create a new project
curl -X POST "http://localhost:8000/api/user/projects" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "Project description"}'

# Generate project documentation
curl -X POST "http://localhost:8000/api/user/projects/{project_id}/generate-brd" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_description": "Detailed project description"}'
```

---

## 🚀 Deployment

### Vercel Deployment

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Configure vercel.json**:
   ```json
   {
     "builds": [
       {
         "src": "run.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "run.py"
       }
     ]
   }
   ```

3. **Set Environment Variables**:
   ```bash
   vercel env add SUPABASE_URL
   vercel env add SUPABASE_KEY
   vercel env add OPENAI_API_KEY
   # Add all required environment variables
   ```

4. **Deploy**:
   ```bash
   vercel --prod
   ```

### Docker Production Deployment

```bash
# Build production image
docker build -t taskflow-backend:latest .

# Run with production configuration
docker run -d \
  --name taskflow-backend \
  -p 80:8000 \
  --env-file .env.production \
  --restart unless-stopped \
  taskflow-backend:latest
```

### Environment Setup for Production

```bash
# Production environment variables
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_KEY=your_production_key
FRONTEND_URL=https://your-frontend-domain.com

# Production AI model configuration
DEFAULT_MODEL_TYPE=openai
DEFAULT_MODEL_ID=gpt-4o-mini

# Security settings
ENABLE_DEBUG_MODE=False
ENABLE_SHOW_TOOL_CALLS=False

# Performance optimization
RESULTS_DIR=/app/results
```

---

## 📚 API Documentation

Comprehensive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`
- **OpenAPI Spec**: `http://localhost:8000/api/openapi.json`

For detailed endpoint documentation, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md).

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_services.py

# Run with coverage
python -m pytest --cov=app

# Test specific AI service
python examples/generate_brd.py
python examples/run_market_validation.py
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Documentation**: [Full API Documentation](./API_DOCUMENTATION.md)
- **Examples**: Check the `examples/` directory for usage examples
- **Issues**: Report bugs and feature requests on GitHub Issues
- **Email**: support@taskflow.dev

---

**Built with ❤️ for the entrepreneurial community**
