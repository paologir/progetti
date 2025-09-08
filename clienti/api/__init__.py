"""
FastAPI Web Interface for Clienti CRM
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.config import get_config
from core.logger import get_logger

# Get configuration
config = get_config()
logger = get_logger()

# Create FastAPI app with config values
app = FastAPI(
    title=config.app.get('name', 'Clienti CRM'),
    description=config.app.get('description', 'Web interface per CRM consulente digital marketing'),
    version=config.app.get('version', '1.0.0'),
    debug=config.server.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates from configuration (ensure absolute paths)
import os
project_root = os.path.dirname(os.path.dirname(__file__))
static_path = os.path.join(project_root, config.server.static_dir)
templates_path = os.path.join(project_root, config.server.templates_dir)

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)

# Logging middleware for web requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if config.logging.web_enabled:
        logger.log_web_access(
            endpoint=str(request.url.path),
            method=request.method,
            ip=request.client.host if request.client else ""
        )
    response = await call_next(request)
    return response

# Import routes
from . import routes