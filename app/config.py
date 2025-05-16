import os
from dotenv import load_dotenv
from supabase import create_client, Client
from .services.brd_generator import BRDGeneratorService
from .services.prd_generator import PRDGeneratorService
from .services.task_generator import TaskGeneratorService
from .services.market_validation import MarketValidationService

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Frontend configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

# API configuration
API_V1_PREFIX = "/api"
PROJECT_NAME = "TaskFlow"
VERSION = "1.0.0"

# CORS configuration
CORS_ORIGINS = [
    FRONTEND_URL,  # Frontend URL
    "http://localhost:8000",  # FastAPI default port
] 

# Initialize AI services once to be reused across the application
# Create singleton service instances
brd_service = BRDGeneratorService()
prd_service = PRDGeneratorService()
task_service = TaskGeneratorService()
market_validation_service = MarketValidationService() 