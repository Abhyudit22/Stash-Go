from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from pydantic import Field
from datetime import datetime



class ProductBase(BaseModel):
    sku: str
    name: str
    cost_price: Decimal
    selling_price: Decimal
    quantity_left: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    quantity_left: Optional[int] = None


class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True



class StockUpdate(BaseModel):
    quantity: int = Field(gt=0)

class SaleCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    customer_name: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    selling_price_at_time: float
    cost_price_at_time: float
    total_amount: float
    profit: float
    customer_name: Optional[str]
    sale_date: datetime
    
    class Config:
        from_attributes = True
