from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import API_V1_PREFIX, PROJECT_NAME, VERSION, CORS_ORIGINS
from .routes.user import auth as user_auth
from .routes.user import project as user_project
from .routes.user import task as user_task
from .routes.user import index as user_info
from .routes.admin import auth as admin_auth
from .routes.super import auth as super_auth

# Create FastAPI app
app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    docs_url=f"{API_V1_PREFIX}/docs",
    redoc_url=f"{API_V1_PREFIX}/redoc",
    openapi_url=f"{API_V1_PREFIX}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include user routers
app.include_router(user_info.router, prefix=f"{API_V1_PREFIX}/user")
app.include_router(user_auth.router, prefix=f"{API_V1_PREFIX}/user")
app.include_router(user_project.router, prefix=f"{API_V1_PREFIX}/user")
app.include_router(user_task.router, prefix=f"{API_V1_PREFIX}/user")

# Include admin routers
app.include_router(admin_auth.router, prefix=f"{API_V1_PREFIX}/admin")

# Include super admin routers
app.include_router(super_auth.router, prefix=f"{API_V1_PREFIX}/super")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": PROJECT_NAME,
        "version": VERSION,
        "message": "Welcome to TaskFlow API"
    } 