from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = True
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[str] = None
    category_ids: Optional[List[int]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    sku: str
    price: float
    stock_quantity: int
    is_active: bool
    weight: Optional[float]
    dimensions: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductSearchResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    pages: int
