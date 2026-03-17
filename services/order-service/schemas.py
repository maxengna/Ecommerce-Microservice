from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]
    total_amount: float = Field(..., gt=0)
    shipping_address: str
    billing_address: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    shipping_address: str
    billing_address: Optional[str]
    tracking_number: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    method: str
    status: str
    transaction_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    order_id: int
    amount: float = Field(..., gt=0)
    method: str
    transaction_id: Optional[str] = None
