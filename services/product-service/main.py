from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from contextlib import asynccontextmanager
import uvicorn
import redis
import pika
import json
from datetime import datetime
from typing import List, Optional

from database import get_db, engine
from models import Base, Product, Category, ProductCategory
from schemas import ProductCreate, ProductResponse, ProductUpdate, CategoryResponse
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
    # Startup
    print("Product Service starting up...")
    yield
    # Shutdown
    print("Product Service shutting down...")

app = FastAPI(
    title="Product Service",
    description="E-commerce Product Management Service",
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
    return {"message": "Product Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-service"}

@app.post("/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Check if product already exists
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    # Create new product
    db_product = Product(
        name=product.name,
        description=product.description,
        sku=product.sku,
        price=product.price,
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
        weight=product.weight,
        dimensions=product.dimensions
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Add categories if provided
    if product.category_ids:
        for category_id in product.category_ids:
            product_category = ProductCategory(
                product_id=db_product.id,
                category_id=category_id
            )
            db.add(product_category)
        db.commit()
    
    # Cache product in Redis
    cache_key = f"product:{db_product.id}"
    product_data = ProductResponse.from_orm(db_product).dict()
    redis_client.setex(cache_key, 3600, json.dumps(product_data))
    
    # Publish product creation event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange='product.events', exchange_type='topic')
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "product.created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "product_id": db_product.id,
                "sku": db_product.sku,
                "name": db_product.name,
                "price": float(db_product.price),
                "stock_quantity": db_product.stock_quantity
            }
        }
        
        channel.basic_publish(
            exchange='product.events',
            routing_key='product.created',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish product creation event: {e}")
    
    return ProductResponse.from_orm(db_product)

@app.get("/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    in_stock: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    # Build query
    query = db.query(Product).filter(Product.is_active == True)
    
    # Apply filters
    if category_id:
        query = query.join(ProductCategory).filter(
            ProductCategory.category_id == category_id
        )
    
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%")
            )
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if in_stock is not None:
        if in_stock:
            query = query.filter(Product.stock_quantity > 0)
        else:
            query = query.filter(Product.stock_quantity == 0)
    
    # Apply pagination
    products = query.offset(skip).limit(limit).all()
    
    return [ProductResponse.from_orm(product) for product in products]

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    # Try to get from cache first
    cache_key = f"product:{product_id}"
    cached_product = redis_client.get(cache_key)
    
    if cached_product:
        return ProductResponse.parse_raw(cached_product)
    
    # Get from database
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Cache the result
    product_data = ProductResponse.from_orm(product).dict()
    redis_client.setex(cache_key, 3600, json.dumps(product_data))
    
    return ProductResponse.from_orm(product)

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Track changes for event
    changes = {}
    old_stock = product.stock_quantity
    
    # Update fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(product, field):
            setattr(product, field, value)
            changes[field] = value
    
    db.commit()
    db.refresh(product)
    
    # Update cache
    cache_key = f"product:{product_id}"
    product_data = ProductResponse.from_orm(product).dict()
    redis_client.setex(cache_key, 3600, json.dumps(product_data))
    
    # Publish product update events
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange='product.events', exchange_type='topic')
        channel.exchange_declare(exchange='inventory.updates', exchange_type='topic')
        
        # Product updated event
        update_message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "product.updated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "product_id": product.id,
                "changes": changes
            }
        }
        
        channel.basic_publish(
            exchange='product.events',
            routing_key='product.updated',
            body=json.dumps(update_message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        # Stock update event if stock changed
        if 'stock_quantity' in changes and old_stock != product.stock_quantity:
            stock_message = {
                "event_id": str(datetime.utcnow()),
                "event_type": "product.stock.updated",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "product_id": product.id,
                    "old_quantity": old_stock,
                    "new_quantity": product.stock_quantity,
                    "sku": product.sku
                }
            }
            
            channel.basic_publish(
                exchange='inventory.updates',
                routing_key='product.stock.updated',
                body=json.dumps(stock_message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        
        connection.close()
    except Exception as e:
        print(f"Failed to publish product update events: {e}")
    
    return ProductResponse.from_orm(product)

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    product.is_active = False
    db.commit()
    
    # Remove from cache
    redis_client.delete(f"product:{product_id}")
    
    # Publish product deletion event
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange='product.events', exchange_type='topic')
        
        message = {
            "event_id": str(datetime.utcnow()),
            "event_type": "product.deleted",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "product_id": product.id,
                "sku": product.sku
            }
        }
        
        channel.basic_publish(
            exchange='product.events',
            routing_key='product.deleted',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish product deletion event: {e}")
    
    return {"message": "Product deleted successfully"}

@app.post("/categories", response_model=CategoryResponse)
async def create_category(name: str, description: str = None, parent_id: int = None, db: Session = Depends(get_db)):
    category = Category(
        name=name,
        description=description,
        parent_id=parent_id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return CategoryResponse.from_orm(category)

@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [CategoryResponse.from_orm(category) for category in categories]

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
