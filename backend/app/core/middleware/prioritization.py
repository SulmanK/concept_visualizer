"""
Request prioritization middleware for the Concept Visualizer API.

This module provides middleware to prioritize concept generation endpoints over
health checks when the server is busy.
"""

import asyncio
import logging
import time
from typing import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.core.exceptions import ApplicationError

# Configure logging
logger = logging.getLogger(__name__)

# Track active generation processes
active_generation_count = 0
generation_semaphore = asyncio.Semaphore(10)  # Limit concurrent generations


class PrioritizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to prioritize concept generation endpoints over health checks.
    
    This middleware gives priority to important endpoints like concept generation
    when the server is busy, potentially delaying health checks and other 
    non-critical requests.
    
    Attributes:
        active_generation_count: Global counter of active generation processes
        generation_semaphore: Semaphore limiting concurrent generations
    """
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process the request with appropriate prioritization.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler in the chain
            
        Returns:
            Response: The HTTP response
        """
        path = request.url.path
        method = request.method
        
        logger.debug(f"Processing request: {method} {path}")
        
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
        start_time = time.time()
        
        try:
            # For high priority endpoints, increment the counter and acquire semaphore
            if is_high_priority:
                logger.debug(f"Processing high priority request: {path}, active generations: {active_generation_count}")
                active_generation_count += 1
                try:
                    # Use the semaphore to limit concurrent generation requests
                    async with generation_semaphore:
                        try:
                            # Process the request with priority
                            response = await call_next(request)
                            process_time = time.time() - start_time
                            response.headers["X-Process-Time"] = str(process_time)
                            logger.debug(f"High priority request completed in {process_time:.2f}s: {path}")
                            return response
                        except Exception as e:
                            logger.error(f"Error processing high priority request: {str(e)}")
                            # Let the exception propagate to be handled by error handlers
                            raise
                finally:
                    # Always decrement the counter, even if there was an error
                    active_generation_count -= 1
            
            # For health checks when server is busy, use a cached response if possible
            elif is_health_check and active_generation_count > 5:
                logger.debug(f"Returning cached health check response due to high load ({active_generation_count} active generations)")
                # If we're very busy with generations, serve a quick cached response for health checks
                return Response(
                    content='{"status":"ok","from_cache":true,"active_generations":' + str(active_generation_count) + '}',
                    media_type="application/json",
                    headers={"X-From-Cache": "true"}
                )
            
            # Session endpoints should not be rate limited at all
            elif is_session_endpoint:
                logger.debug(f"Processing session request: {path}")
                # Process session requests normally, without any rate limiting
                response = await call_next(request)
                process_time = time.time() - start_time
                response.headers["X-Process-Time"] = str(process_time)
                logger.debug(f"Session request completed in {process_time:.2f}s: {path}")
                return response
            
            # For other endpoints, process normally
            else:
                logger.debug(f"Processing standard request: {path}")
                response = await call_next(request)
                process_time = time.time() - start_time
                response.headers["X-Process-Time"] = str(process_time)
                logger.debug(f"Standard request completed in {process_time:.2f}s: {path}")
                return response
                
        except Exception as e:
            # Log the error but don't handle it - let it propagate to FastAPI's error handlers
            process_time = time.time() - start_time
            logger.error(f"Error in prioritization middleware ({process_time:.2f}s): {str(e)}")
            
            # For security reasons, we don't want to expose internal errors directly
            # So we'll create a generic error response for true 500 errors
            # For ApplicationErrors, they should be caught by a proper error handler later
            if not isinstance(e, ApplicationError):
                # Very basic error response for truly unexpected errors
                # This will be rare as most errors should be caught and processed by error handlers
                return Response(
                    content='{"error":true,"detail":"Internal server error","status_code":500}',
                    media_type="application/json",
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                    headers={"X-Process-Time": str(process_time)}
                )
            
            # Let application errors (and others) propagate to be handled by the error handlers
            raise 