from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Service URLs
    USER_SERVICE_URL: str = "http://user-service:8001"
    PRODUCT_SERVICE_URL: str = "http://product-service:8002"
    ORDER_SERVICE_URL: str = "http://order-service:8003"
    CART_SERVICE_URL: str = "http://cart-service:8004"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8005"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT: str = "100/minute"
    
    # Service
    SERVICE_NAME: str = "api-gateway"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
