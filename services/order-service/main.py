from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
import redis
import pika
import json
import stripe
from datetime import datetime
from typing import List, Optional

from database import get_db, engine
from models import Base, Order, OrderItem, Payment
from schemas import OrderCreate, OrderResponse, OrderItemResponse, PaymentResponse
from config import settings

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

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
        channel.exchange_declare(exchange='order.events', exchange_type='topic')
        channel.exchange_declare(exchange='payments.processing', exchange_type='topic')
        
        # Declare queues
        channel.queue_declare(queue='order_processing', durable=True)
        channel.queue_declare(queue='payment_processing', durable=True)
        
        # Bind queues to exchanges
        channel.queue_bind(exchange='order.events', queue='order_processing', routing_key='order.*')
        channel.queue_bind(exchange='payments.processing', queue='payment_processing', routing_key='payment.*')
        
        connection.close()
        print("Order Service: RabbitMQ setup completed")
    except Exception as e:
        print(f"Failed to setup RabbitMQ: {e}")
    
    yield
    print("Order Service shutting down...")

app = FastAPI(
    title="Order Service",
    description="E-commerce Order Management Service",
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
    return {"message": "Order Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}

@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Create order
    db_order = Order(
        user_id=order.user_id,
        total_amount=order.total_amount,
        status="pending",
        shipping_address=order.shipping_address,
        billing_address=order.billing_address
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items
    for item in order.items:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(order_item)
    
    db.commit()
    
    # Cache order in Redis
    cache_key = f"order:{db_order.id}"
    order_data = OrderResponse.from_orm(db_order).dict()
    redis_client.setex(cache_key, 3600, json.dumps(order_data))
    
    # Publish order created event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "order.created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "order_id": db_order.id,
                "user_id": db_order.user_id,
                "total_amount": float(db_order.total_amount),
                "status": db_order.status,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": float(item.price)
                    }
                    for item in order.items
                ]
            }
        }
        
        channel.basic_publish(
            exchange='order.events',
            routing_key='order.created',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish order creation event: {e}")
    
    return OrderResponse.from_orm(db_order)

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    # Try cache first
    cache_key = f"order:{order_id}"
    cached_order = redis_client.get(cache_key)
    
    if cached_order:
        return OrderResponse.parse_raw(cached_order)
    
    # Get from database
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Cache result
    order_data = OrderResponse.from_orm(order).dict()
    redis_client.setex(cache_key, 3600, json.dumps(order_data))
    
    return OrderResponse.from_orm(order)

@app.get("/users/{user_id}/orders", response_model=List[OrderResponse])
async def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return [OrderResponse.from_orm(order) for order in orders]

@app.post("/orders/{order_id}/payments")
async def create_payment(
    order_id: int,
    payment_method: str,
    payment_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Create payment record
    payment = Payment(
        order_id=order_id,
        amount=order.total_amount,
        method=payment_method,
        status="processing"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Process payment based on method
    if payment_method == "stripe" and payment_token:
        try:
            # Create Stripe charge
            charge = stripe.Charge.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency="usd",
                source=payment_token,
                description=f"Order {order_id}"
            )
            
            if charge.status == "succeeded":
                payment.status = "completed"
                payment.transaction_id = charge.id
                order.status = "paid"
                
                # Publish payment success event
                await publish_payment_event(
                    "payment.completed",
                    payment.id,
                    order_id,
                    order.total_amount,
                    charge.id
                )
            else:
                payment.status = "failed"
                order.status = "payment_failed"
                
                await publish_payment_event(
                    "payment.failed",
                    payment.id,
                    order_id,
                    order.total_amount,
                    charge.id
                )
            
        except stripe.error.StripeError as e:
            payment.status = "failed"
            order.status = "payment_failed"
            print(f"Stripe payment failed: {e}")
    
    elif payment_method == "cash_on_delivery":
        payment.status = "pending"
        order.status = "confirmed"
        
        await publish_payment_event(
            "payment.pending",
            payment.id,
            order_id,
            order.total_amount,
            None
        )
    
    db.commit()
    
    # Update cache
    cache_key = f"order:{order_id}"
    order_data = OrderResponse.from_orm(order).dict()
    redis_client.setex(cache_key, 3600, json.dumps(order_data))
    
    return PaymentResponse.from_orm(payment)

async def publish_payment_event(event_type: str, payment_id: int, order_id: int, amount: float, transaction_id: Optional[str]):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "payment_id": payment_id,
                "order_id": order_id,
                "amount": float(amount),
                "transaction_id": transaction_id
            }
        }
        
        channel.basic_publish(
            exchange='payments.processing',
            routing_key='payment.updated',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish payment event: {e}")

@app.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    old_status = order.status
    order.status = new_status
    db.commit()
    
    # Publish status update event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "order.status_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "order_id": order_id,
                "old_status": old_status,
                "new_status": new_status
            }
        }
        
        channel.basic_publish(
            exchange='order.events',
            routing_key='order.status_updated',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish status update event: {e}")
    
    # Update cache
    cache_key = f"order:{order_id}"
    order_data = OrderResponse.from_orm(order).dict()
    redis_client.setex(cache_key, 3600, json.dumps(order_data))
    
    return {"message": f"Order status updated to {new_status}"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
