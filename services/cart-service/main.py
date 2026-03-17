from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
import redis
import pika
import json
from datetime import datetime
from typing import List, Optional

from database import get_db, engine
from models import Base, Cart, CartItem
from schemas import CartItemCreate, CartItemResponse, CartResponse
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup RabbitMQ queues and exchanges on startup
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declare exchanges
        channel.exchange_declare(exchange='cart.events', exchange_type='topic')
        
        # Declare queues
        channel.queue_declare(queue='cart_processing', durable=True)
        
        # Bind queues to exchanges
        channel.queue_bind(exchange='cart.events', queue='cart_processing', routing_key='cart.*')
        
        connection.close()
        print("Cart Service: RabbitMQ setup completed")
    except Exception as e:
        print(f"Failed to setup RabbitMQ: {e}")
    
    yield
    print("Cart Service shutting down...")

app = FastAPI(
    title="Cart Service",
    description="E-commerce Shopping Cart Management Service",
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

@app.get("/")
async def root():
    return {"message": "Cart Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cart-service"}

@app.get("/cart/{user_id}", response_model=CartResponse)
async def get_cart(user_id: int, db: Session = Depends(get_db)):
    # Try cache first
    cache_key = f"cart:{user_id}"
    cached_cart = redis_client.get(cache_key)
    
    if cached_cart:
        return CartResponse.parse_raw(cached_cart)
    
    # Get or create cart from database
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    
    if not cart:
        # Create new cart for user
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Get cart items
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    
    # Build response
    cart_response = CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=[
            CartItemResponse(
                id=item.id,
                cart_id=item.cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                added_at=item.added_at
            )
            for item in cart_items
        ],
        total_amount=sum(item.price * item.quantity for item in cart_items),
        created_at=cart.created_at
    )
    
    # Cache the result
    redis_client.setex(cache_key, 1800, cart_response.json())  # 30 minutes cache
    
    return cart_response

@app.post("/cart/{user_id}/items", response_model=CartItemResponse)
async def add_to_cart(
    user_id: int,
    item: CartItemCreate,
    db: Session = Depends(get_db)
):
    # Get or create cart
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Check if item already exists in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item.product_id
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        cart_item = existing_item
    else:
        # Add new item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
    
    # Clear cache
    redis_client.delete(f"cart:{user_id}")
    
    # Publish cart update event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "cart.item_added",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "user_id": user_id,
                "cart_id": cart.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": float(item.price)
            }
        }
        
        channel.basic_publish(
            exchange='cart.events',
            routing_key='cart.item_added',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish cart update event: {e}")
    
    return CartItemResponse.from_orm(cart_item)

@app.put("/cart/{user_id}/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    user_id: int,
    item_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )
    
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Verify cart belongs to user
    cart = db.query(Cart).filter(Cart.id == cart_item.cart_id, Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found for this user"
        )
    
    # Update quantity
    old_quantity = cart_item.quantity
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    
    # Clear cache
    redis_client.delete(f"cart:{user_id}")
    
    # Publish cart update event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "cart.item_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "user_id": user_id,
                "cart_id": cart.id,
                "item_id": item_id,
                "old_quantity": old_quantity,
                "new_quantity": quantity,
                "product_id": cart_item.product_id
            }
        }
        
        channel.basic_publish(
            exchange='cart.events',
            routing_key='cart.item_updated',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish cart update event: {e}")
    
    return CartItemResponse.from_orm(cart_item)

@app.delete("/cart/{user_id}/items/{item_id}")
async def remove_from_cart(user_id: int, item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Verify cart belongs to user
    cart = db.query(Cart).filter(Cart.id == cart_item.cart_id, Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found for this user"
        )
    
    # Store product info for event
    product_id = cart_item.product_id
    quantity = cart_item.quantity
    
    # Remove item
    db.delete(cart_item)
    db.commit()
    
    # Clear cache
    redis_client.delete(f"cart:{user_id}")
    
    # Publish cart update event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "cart.item_removed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "user_id": user_id,
                "cart_id": cart.id,
                "product_id": product_id,
                "quantity": quantity
            }
        }
        
        channel.basic_publish(
            exchange='cart.events',
            routing_key='cart.item_removed',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish cart update event: {e}")
    
    return {"message": "Item removed from cart"}

@app.delete("/cart/{user_id}")
async def clear_cart(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    # Get all items before deletion for event
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    
    # Delete all cart items
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    
    # Clear cache
    redis_client.delete(f"cart:{user_id}")
    
    # Publish cart cleared event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "cart.cleared",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "user_id": user_id,
                "cart_id": cart.id,
                "items_count": len(cart_items)
            }
        }
        
        channel.basic_publish(
            exchange='cart.events',
            routing_key='cart.cleared',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish cart cleared event: {e}")
    
    return {"message": "Cart cleared successfully"}

@app.get("/cart/{user_id}/count")
async def get_cart_items_count(user_id: int, db: Session = Depends(get_db)):
    # Try cache first
    cache_key = f"cart_count:{user_id}"
    cached_count = redis_client.get(cache_key)
    
    if cached_count:
        return {"count": int(cached_count)}
    
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        count = 0
    else:
        count = db.query(CartItem).filter(CartItem.cart_id == cart.id).count()
    
    # Cache the count for 5 minutes
    redis_client.setex(cache_key, 300, str(count))
    
    return {"count": count}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
