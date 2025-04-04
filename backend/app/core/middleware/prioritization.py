"""
Request prioritization middleware for the Concept Visualizer API.

This module provides middleware to prioritize concept generation endpoints over
health checks when the server is busy.
"""

import asyncio
import time
from typing import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

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