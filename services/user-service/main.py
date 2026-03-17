from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
import redis
import pika
import json
from datetime import datetime, timedelta
from typing import Optional

from database import get_db, engine
from models import Base, User, UserProfile
from schemas import UserCreate, UserResponse, UserLogin, Token
from auth import create_access_token, verify_token, get_password_hash, verify_password
from config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# RabbitMQ connection
def get_rabbitmq_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            credentials=pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
        )
    )
    return connection

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("User Service starting up...")
    yield
    # Shutdown
    print("User Service shutting down...")

app = FastAPI(
    title="User Service",
    description="E-commerce User Management Service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@app.get("/")
async def root():
    return {"message": "User Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}

@app.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        role=user.role or "customer"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create user profile
    profile = UserProfile(
        user_id=db_user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone
    )
    db.add(profile)
    db.commit()
    
    # Publish user registration event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange='user.events', exchange_type='topic')
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "user.registered",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "user_id": db_user.id,
                "email": db_user.email,
                "role": db_user.role
            }
        }
        
        channel.basic_publish(
            exchange='user.events',
            routing_key='user.registered',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish user registration event: {e}")
    
    return UserResponse.from_orm(db_user)

@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    # Cache user session in Redis
    redis_client.setex(
        f"session:{user.id}",
        timedelta(hours=24),
        json.dumps({"token": access_token, "role": user.role})
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

@app.put("/me", response_model=UserResponse)
async def update_user_profile(
    profile_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    for key, value in profile_update.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    
    # Publish user profile update event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange='user.events', exchange_type='topic')
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "user.profile_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "user_id": current_user.id,
                "updated_fields": list(profile_update.keys())
            }
        }
        
        channel.basic_publish(
            exchange='user.events',
            routing_key='user.profile_updated',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish profile update event: {e}")
    
    return UserResponse.from_orm(current_user)

@app.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # Remove session from Redis
    redis_client.delete(f"session:{current_user.id}")
    return {"message": "Successfully logged out"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
