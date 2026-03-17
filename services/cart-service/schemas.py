from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int
    price: float
    added_at: datetime
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]
    total_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class CartUpdate(BaseModel):
    quantity: int = Field(..., gt=0)
