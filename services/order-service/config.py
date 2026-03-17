from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5432/ecommerce"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379"
    
    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "admin"
    RABBITMQ_PASSWORD: str = "admin123"
    RABBITMQ_URL: str = "amqp://admin:admin123@localhost:5672/"
    
    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_dummy_key_change_in_production"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_dummy_key_change_in_production"
    
    # Service
    SERVICE_NAME: str = "order-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
