"""
Configuration settings for AI services.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration for memory and storage
POSTGRES_CONNECTION = os.getenv("POSTGRES_CONNECTION", None)

# Optional ENVs for OpenAI Like Model
OPENAI_LIKE_BASE_URL = os.getenv("OPENAI_LIKE_BASE_URL", "https://api.openai.com/v1")
OPENAI_LIKE_API_KEY = os.getenv("OPENAI_LIKE_API_KEY", None)

# Default model settings
DEFAULT_MODEL_TYPE = os.getenv("DEFAULT_MODEL_TYPE", "groq")
DEFAULT_MODEL_ID = os.getenv("DEFAULT_MODEL_ID", "llama-3.3-70b-versatile")

# PRD Generator model settings
PRD_MODEL_TYPE = os.getenv("PRD_MODEL_TYPE", DEFAULT_MODEL_TYPE)
PRD_MODEL_ID = os.getenv("PRD_MODEL_ID", DEFAULT_MODEL_ID)

# BRD Generator model settings
BRD_MODEL_TYPE = os.getenv("BRD_MODEL_TYPE", DEFAULT_MODEL_TYPE)
BRD_MODEL_ID = os.getenv("BRD_MODEL_ID", DEFAULT_MODEL_ID)

# Task Generator model settings
TASK_MODEL_TYPE = os.getenv("TASK_MODEL_TYPE", DEFAULT_MODEL_TYPE)
TASK_MODEL_ID = os.getenv("TASK_MODEL_ID", DEFAULT_MODEL_ID)

# GitHub Setup model settings
GITHUB_MODEL_TYPE = os.getenv("GITHUB_MODEL_TYPE", DEFAULT_MODEL_TYPE)
GITHUB_MODEL_ID = os.getenv("GITHUB_MODEL_ID", DEFAULT_MODEL_ID)

# Market Validation model settings
MARKET_RESEARCH_MODEL_TYPE = os.getenv("MARKET_RESEARCH_MODEL_TYPE", "gemini")
MARKET_RESEARCH_MODEL_ID = os.getenv("MARKET_RESEARCH_MODEL_ID", "gemini-2.5-flash-preview-04-17")

MARKET_ANALYSIS_MODEL_TYPE = os.getenv("MARKET_ANALYSIS_MODEL_TYPE", "openai")
MARKET_ANALYSIS_MODEL_ID = os.getenv("MARKET_ANALYSIS_MODEL_ID", "gpt-4o-mini")

REPORT_GENERATOR_MODEL_TYPE = os.getenv("REPORT_GENERATOR_MODEL_TYPE", "openai")
REPORT_GENERATOR_MODEL_ID = os.getenv("REPORT_GENERATOR_MODEL_ID", "gpt-4.1-mini-2025-04-14")

MARKET_VALIDATION_MANAGER_MODEL_TYPE = os.getenv("MARKET_VALIDATION_MANAGER_MODEL_TYPE", "openai")
MARKET_VALIDATION_MANAGER_MODEL_ID = os.getenv("MARKET_VALIDATION_MANAGER_MODEL_ID", "gpt-4o-mini")

# Preview Generator model settings
PREVIEW_MODEL_TYPE = os.getenv("PREVIEW_MODEL_TYPE", DEFAULT_MODEL_TYPE)
PREVIEW_MODEL_ID = os.getenv("PREVIEW_MODEL_ID", DEFAULT_MODEL_ID)

# Service settings
ENABLE_DEBUG_MODE = os.getenv("ENABLE_DEBUG_MODE", "False").lower() == "true"
ENABLE_SHOW_TOOL_CALLS = os.getenv("ENABLE_SHOW_TOOL_CALLS", "True").lower() == "true"
ENABLE_MARKDOWN = os.getenv("ENABLE_MARKDOWN", "True").lower() == "true"

# File paths
RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
os.makedirs(RESULTS_DIR, exist_ok=True) 