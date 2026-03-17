from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
import redis
import pika
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio
import threading

from database import get_db, engine
from models import Base, Notification, NotificationTemplate
from schemas import NotificationCreate, NotificationResponse, EmailTemplate
from config import settings
from email_service import EmailService

# Create database tables
Base.metadata.create_all(bind=engine)

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# Email service
email_service = EmailService()

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

# Message consumer function
def start_message_consumer():
    def consume_messages():
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            
            # Declare exchanges
            channel.exchange_declare(exchange='notifications.email', exchange_type='topic')
            channel.exchange_declare(exchange='order.events', exchange_type='topic')
            channel.exchange_declare(exchange='user.events', exchange_type='topic')
            channel.exchange_declare(exchange='cart.events', exchange_type='topic')
            
            # Declare queue
            channel.queue_declare(queue='notification_processing', durable=True)
            
            # Bind queue to exchanges
            channel.queue_bind(exchange='notifications.email', queue='notification_processing', routing_key='email.*')
            channel.queue_bind(exchange='order.events', queue='notification_processing', routing_key='order.*')
            channel.queue_bind(exchange='user.events', queue='notification_processing', routing_key='user.*')
            channel.queue_bind(exchange='cart.events', queue='notification_processing', routing_key='cart.*')
            
            def callback(ch, method, properties, body):
                try:
                    message = json.loads(body)
                    asyncio.run(process_notification_message(message))
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            channel.basic_consume(queue='notification_processing', on_message_callback=callback)
            print("Notification Service: Started consuming messages")
            channel.start_consuming()
            
        except Exception as e:
            print(f"Error in message consumer: {e}")
            time.sleep(5)
            consume_messages()  # Retry connection
    
    # Start consumer in separate thread
    consumer_thread = threading.Thread(target=consume_messages, daemon=True)
    consumer_thread.start()

async def process_notification_message(message: dict):
    """Process incoming notification messages from RabbitMQ"""
    event_type = message.get('event_type')
    data = message.get('data', {})
    
    try:
        if event_type == 'order.created':
            await send_order_confirmation_email(data)
        elif event_type == 'order.status_updated':
            await send_order_status_update_email(data)
        elif event_type == 'user.registered':
            await send_welcome_email(data)
        elif event_type == 'payment.completed':
            await send_payment_confirmation_email(data)
        elif event_type == 'cart.abandoned':
            await send_cart_abandoned_email(data)
        else:
            print(f"Unknown event type: {event_type}")
    except Exception as e:
        print(f"Error processing notification: {e}")

async def send_order_confirmation_email(order_data: dict):
    """Send order confirmation email"""
    template = await get_email_template('order_confirmation')
    if not template:
        return
    
    # Get user email (would typically call user service)
    user_email = f"user{order_data.get('user_id')}@example.com"  # Placeholder
    
    subject = template.subject.replace('{{order_id}}', str(order_data.get('order_id')))
    body = template.body.replace('{{order_id}}', str(order_data.get('order_id')))
    body = body.replace('{{total_amount}}', str(order_data.get('total_amount')))
    
    await create_notification(
        user_id=order_data.get('user_id'),
        type='email',
        subject=subject,
        content=body,
        recipient=user_email,
        status='pending'
    )

async def send_welcome_email(user_data: dict):
    """Send welcome email to new user"""
    template = await get_email_template('welcome')
    if not template:
        return
    
    user_email = user_data.get('email')
    
    subject = template.subject
    body = template.body.replace('{{user_email}}', user_email)
    
    await create_notification(
        user_id=user_data.get('user_id'),
        type='email',
        subject=subject,
        content=body,
        recipient=user_email,
        status='pending'
    )

async def get_email_template(template_name: str):
    """Get email template from database or return default"""
    # For now, return default templates
    templates = {
        'order_confirmation': EmailTemplate(
            subject='Order Confirmation #{{order_id}}',
            body='Thank you for your order! Your order #{{order_id}} has been received. Total: ${{total_amount}}'
        ),
        'welcome': EmailTemplate(
            subject='Welcome to E-Shop!',
            body='Welcome {{user_email}}! Thank you for registering with E-Shop. We\'re excited to have you!'
        ),
        'order_status': EmailTemplate(
            subject='Order Status Update',
            body='Your order status has been updated. Order ID: {{order_id}}'
        ),
        'payment_confirmation': EmailTemplate(
            subject='Payment Confirmation',
            body='Your payment has been successfully processed. Order ID: {{order_id}}'
        )
    }
    return templates.get(template_name)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start message consumer
    start_message_consumer()
    
    print("Notification Service starting up...")
    yield
    print("Notification Service shutting down...")

app = FastAPI(
    title="Notification Service",
    description="E-commerce Notification Management Service",
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
    return {"message": "Notification Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}

async def create_notification(
    user_id: int,
    type: str,
    subject: str,
    content: str,
    recipient: str,
    status: str = 'pending',
    db: Session = None
):
    """Create notification record"""
    if not db:
        from database import SessionLocal
        db = SessionLocal()
        try:
            notification = Notification(
                user_id=user_id,
                type=type,
                subject=subject,
                content=content,
                recipient=recipient,
                status=status
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Schedule email sending
            if type == 'email':
                await send_email_async(notification.id)
            
            return notification
        finally:
            db.close()
    else:
        notification = Notification(
            user_id=user_id,
            type=type,
            subject=subject,
            content=content,
            recipient=recipient,
            status=status
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Schedule email sending
        if type == 'email':
            await send_email_async(notification.id)
        
        return notification

async def send_email_async(notification_id: int):
    """Send email asynchronously"""
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification or notification.status != 'pending':
            return
        
        # Send email
        success = await email_service.send_email(
            to_email=notification.recipient,
            subject=notification.subject,
            body=notification.content
        )
        
        # Update notification status
        if success:
            notification.status = 'sent'
            notification.sent_at = datetime.utcnow()
        else:
            notification.status = 'failed'
            notification.error_message = 'Failed to send email'
        
        db.commit()
        
    except Exception as e:
        print(f"Error sending email: {e}")
        notification.status = 'failed'
        notification.error_message = str(e)
        db.commit()
    finally:
        db.close()

@app.post("/notifications", response_model=NotificationResponse)
async def send_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send notification manually"""
    db_notification = await create_notification(
        user_id=notification.user_id,
        type=notification.type,
        subject=notification.subject,
        content=notification.content,
        recipient=notification.recipient,
        db=db
    )
    
    return NotificationResponse.from_orm(db_notification)

@app.get("/notifications/{user_id}", response_model=List[NotificationResponse])
async def get_user_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get notifications for a user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return [NotificationResponse.from_orm(notification) for notification in notifications]

@app.get("/notifications", response_model=List[NotificationResponse])
async def get_all_notifications(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all notifications (admin)"""
    query = db.query(Notification)
    
    if status:
        query = query.filter(Notification.status == status)
    
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return [NotificationResponse.from_orm(notification) for notification in notifications]

@app.post("/test-email")
async def test_email():
    """Test email functionality"""
    try:
        success = await email_service.send_email(
            to_email="test@example.com",
            subject="Test Email",
            body="This is a test email from the notification service."
        )
        
        return {"message": "Test email sent successfully" if success else "Failed to send test email"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )
