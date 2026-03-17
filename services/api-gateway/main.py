from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx
import redis
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
import logging

from config import settings
from auth import verify_token
from middleware import auth_middleware, logging_middleware

# Redis connection for rate limiting and caching
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
SERVICES = {
    "user": settings.USER_SERVICE_URL,
    "product": settings.PRODUCT_SERVICE_URL,
    "order": settings.ORDER_SERVICE_URL,
    "cart": settings.CART_SERVICE_URL,
    "notification": settings.NOTIFICATION_SERVICE_URL,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Gateway starting up...")
    yield
    logger.info("API Gateway shutting down...")

app = FastAPI(
    title="E-commerce API Gateway",
    description="Gateway for all microservices",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiting exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(auth_middleware)
app.middleware("http")(logging_middleware)

# Service registry with health checks
service_health: Dict[str, bool] = {}

async def check_service_health():
    """Check health of all services"""
    for service_name, url in SERVICES.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5.0)
                service_health[service_name] = response.status_code == 200
        except Exception:
            service_health[service_name] = False

# Health check endpoint
@app.get("/health")
async def health_check():
    await check_service_health()
    return {
        "status": "healthy",
        "services": service_health,
        "timestamp": time.time()
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "E-commerce API Gateway",
        "version": "1.0.0",
        "services": list(SERVICES.keys())
    }

# Proxy routes
@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("100/minute")
async def auth_proxy(request: Request, path: str):
    """Proxy authentication requests to user service"""
    return await proxy_request(request, "user", f"/{path}")

@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("200/minute")
async def user_proxy(request: Request, path: str):
    """Proxy user-related requests to user service"""
    return await proxy_request(request, "user", f"/{path}")

@app.api_route("/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("500/minute")
async def product_proxy(request: Request, path: str):
    """Proxy product requests to product service"""
    return await proxy_request(request, "product", f"/{path}")

@app.api_route("/categories/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("200/minute")
async def category_proxy(request: Request, path: str):
    """Proxy category requests to product service"""
    return await proxy_request(request, "product", f"/{path}")

@app.api_route("/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("100/minute")
async def order_proxy(request: Request, path: str):
    """Proxy order requests to order service"""
    return await proxy_request(request, "order", f"/{path}")

@app.api_route("/cart/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("300/minute")
async def cart_proxy(request: Request, path: str):
    """Proxy cart requests to cart service"""
    return await proxy_request(request, "cart", f"/{path}")

@app.api_route("/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("50/minute")
async def notification_proxy(request: Request, path: str):
    """Proxy notification requests to notification service"""
    return await proxy_request(request, "notification", f"/{path}")

async def proxy_request(request: Request, service: str, path: str):
    """Proxy request to appropriate microservice"""
    service_url = SERVICES.get(service)
    if not service_url:
        raise HTTPException(
            status_code=503,
            detail=f"Service {service} not available"
        )
    
    # Check service health
    if not service_health.get(service, False):
        raise HTTPException(
            status_code=503,
            detail=f"Service {service} is unhealthy"
        )
    
    # Build target URL
    target_url = f"{service_url}{path}"
    if request.query_params:
        target_url += f"?{request.url.query}"
    
    try:
        # Prepare request data
        headers = dict(request.headers)
        headers.pop("host", None)  # Remove host header
        
        # Forward request
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body(),
                timeout=30.0
            )
        
        # Return response
        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"Service {service} timeout"
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to service {service}"
        )
    except Exception as e:
        logger.error(f"Error proxying to {service}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# API Documentation endpoints
@app.get("/docs")
async def api_docs():
    """API documentation"""
    return {
        "title": "E-commerce API Gateway",
        "version": "1.0.0",
        "services": {
            "user": {
                "url": "/auth/*, /users/*",
                "description": "User authentication and management"
            },
            "product": {
                "url": "/products/*, /categories/*",
                "description": "Product catalog management"
            },
            "order": {
                "url": "/orders/*",
                "description": "Order processing and management"
            },
            "cart": {
                "url": "/cart/*",
                "description": "Shopping cart management"
            },
            "notification": {
                "url": "/notifications/*",
                "description": "Notification management"
            }
        }
    }

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Basic metrics for monitoring"""
    await check_service_health()
    
    return {
        "services": {
            name: {
                "healthy": health,
                "url": url
            }
            for name, (health, url) in zip(
                service_health.keys(),
                [(service_health.get(name, False), SERVICES.get(name, "")) for name in service_health.keys()]
            )
        },
        "gateway": {
            "uptime": time.time(),
            "version": "1.0.0"
        }
    }

# Service discovery endpoint
@app.get("/services")
async def list_services():
    """List all available services"""
    await check_service_health()
    return {
        "services": [
            {
                "name": name,
                "url": url,
                "healthy": service_health.get(name, False)
            }
            for name, url in SERVICES.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
