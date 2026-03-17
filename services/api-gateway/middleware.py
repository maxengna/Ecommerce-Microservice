from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
import json
from typing import Dict, Any
from auth import extract_token_from_header, get_user_from_token

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for API Gateway"""
    
    # Paths that don't require authentication
    PUBLIC_PATHS = {
        "/",
        "/health",
        "/metrics",
        "/services",
        "/docs",
        "/auth/login",
        "/auth/register",
        "/products",
        "/categories",
    }
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Skip authentication for public paths
        if self.is_public_path(path):
            return await call_next(request)
        
        # Check for authentication
        authorization = request.headers.get("authorization")
        token = extract_token_from_header(authorization) if authorization else None
        
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )
        
        # Verify token
        user_info = get_user_from_token(token)
        if not user_info:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"}
            )
        
        # Add user info to request state
        request.state.user = user_info
        
        response = await call_next(request)
        return response
    
    def is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require authentication)"""
        # Check exact matches
        if path in self.PUBLIC_PATHS:
            return True
        
        # Check path prefixes
        for public_path in self.PUBLIC_PATHS:
            if public_path.endswith("*") and path.startswith(public_path[:-1]):
                return True
            if path.startswith(public_path) and (
                public_path.endswith("/") or 
                len(path) == len(public_path) or 
                path[len(public_path)] == "/"
            ):
                return True
        
        return False

class LoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, redis_client, default_limit: str = "100/minute"):
        super().__init__(app)
        self.redis_client = redis_client
        self.default_limit = default_limit
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Get rate limit for this path
        rate_limit = self.get_rate_limit(request.url.path)
        
        # Check rate limit
        if not await self.check_rate_limit(client_ip, rate_limit):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"}
            )
        
        return await call_next(request)
    
    def get_rate_limit(self, path: str) -> str:
        """Get rate limit for specific path"""
        # Different limits for different endpoints
        if path.startswith("/auth/"):
            return "50/minute"
        elif path.startswith("/products/"):
            return "500/minute"
        elif path.startswith("/orders/"):
            return "100/minute"
        elif path.startswith("/cart/"):
            return "300/minute"
        else:
            return self.default_limit
    
    async def check_rate_limit(self, client_ip: str, rate_limit: str) -> bool:
        """Check if client is within rate limit"""
        try:
            # Parse rate limit (e.g., "100/minute")
            limit, period = rate_limit.split("/")
            limit = int(limit)
            
            # Convert period to seconds
            period_seconds = {
                "second": 1,
                "minute": 60,
                "hour": 3600,
                "day": 86400
            }.get(period, 60)
            
            # Redis key
            key = f"rate_limit:{client_ip}:{rate_limit}"
            
            # Get current count
            current = self.redis_client.get(key)
            
            if current is None:
                # First request in this period
                self.redis_client.setex(key, period_seconds, 1)
                return True
            else:
                current = int(current)
                if current >= limit:
                    return False
                else:
                    self.redis_client.incr(key)
                    return True
                    
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Allow request if rate limiting fails
            return True

# Middleware instances for use in main app
auth_middleware = AuthMiddleware
logging_middleware = LoggingMiddleware
