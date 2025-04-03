"""
Main application entry point for the Concept Visualizer API.

This module initializes the FastAPI application and includes all routes.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import configure_api_routes
from app.core.config import settings
from app.utils.logging import setup_logging
from app.core.rate_limiter import setup_rate_limiter

# Configure application logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Concept Visualizer API",
    description=(
        "API for generating and refining visual concepts using JigsawStack. "
        "This API provides endpoints for creating logo designs with matching "
        "color palettes and refining existing designs based on user feedback."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Concept Visualizer Team",
        "url": "https://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Setup rate limiting
limiter = setup_rate_limiter(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track active generation processes
active_generation_count = 0
generation_semaphore = asyncio.Semaphore(10)  # Limit concurrent generations

class PrioritizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to prioritize concept generation endpoints over health checks.
    
    This middleware gives priority to important endpoints like concept generation
    when the server is busy, potentially delaying health checks and other 
    non-critical requests.
    """
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        # Identify if this is a heavy endpoint (concept generation/refinement)
        is_high_priority = (
            ("/api/concept/generate" in path or 
             "/api/concept/refine" in path or 
             "/api/concepts/generate-with-palettes" in path) and
            method == "POST"
        )
        
        # Identify if this is a health check or session endpoint (low priority)
        is_health_check = ("/api/health" in path and method in ["GET", "HEAD"])
        is_session_endpoint = "/api/session" in path
        
        global active_generation_count
        
        # For high priority endpoints, increment the counter and acquire semaphore
        if is_high_priority:
            active_generation_count += 1
            async with generation_semaphore:
                try:
                    # Process the request with priority
                    start_time = time.time()
                    response = await call_next(request)
                    process_time = time.time() - start_time
                    response.headers["X-Process-Time"] = str(process_time)
                    return response
                finally:
                    active_generation_count -= 1
        
        # For health checks when server is busy, use a cached response if possible
        elif is_health_check and active_generation_count > 5:
            # If we're very busy with generations, serve a quick cached response for health checks
            return Response(
                content='{"status":"ok"}',
                media_type="application/json",
                headers={"X-From-Cache": "true"}
            )
        
        # Session endpoints should not be rate limited at all
        elif is_session_endpoint:
            # Process session requests normally, without any rate limiting
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        
        # For other endpoints, process normally
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

# Add prioritization middleware
app.add_middleware(PrioritizationMiddleware)

# Configure API routes and error handlers
configure_api_routes(app)

@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns information about the API and links to documentation.
    """
    return {
        "message": "Welcome to the Concept Visualizer API",
        "documentation": "/docs",
        "redoc": "/redoc",
        "api_prefix": settings.API_PREFIX,
        "version": "0.1.0",
    } 