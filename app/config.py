import os
from dotenv import load_dotenv
from supabase import create_client, Client

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