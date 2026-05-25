from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# Product Schemas
class ProductCreate(BaseModel):
    sku: str
    name: str
    cost_price: float = Field(gt=0)
    selling_price: float = Field(gt=0)
    quantity_left: int = Field(ge=0)


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    cost_price: Optional[float] = Field(None, gt=0)
    selling_price: Optional[float] = Field(None, gt=0)
    quantity_left: Optional[int] = Field(None, ge=0)


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    cost_price: float
    selling_price: float
    quantity_left: int
    
    class Config:
        from_attributes = True


# Stock Update Schema
class StockUpdate(BaseModel):
    quantity: int = Field(gt=0)


# Sale Schemas
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


# Return Schemas
class ReturnCreate(BaseModel):
    sale_id: int
    product_id: int
    quantity: int = Field(gt=0)
    reason: str


class ReturnResponse(BaseModel):
    id: int
    sale_id: int
    product_id: int
    product_name: str
    quantity: int
    reason: str
    refund_amount: float
    return_date: datetime
    
    class Config:
        from_attributes = True


# Bill Schemas
class BillCreate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None


class BillItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class BillUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    discount: Optional[float] = Field(default=0, ge=0)
    tax: Optional[float] = Field(default=0, ge=0)
    payment_method: Optional[str] = None


class BillItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    
    class Config:
        from_attributes = True


class BillResponse(BaseModel):
    id: int
    bill_number: str
    customer_name: Optional[str]
    customer_phone: Optional[str]
    customer_email: Optional[str]
    created_date: datetime
    status: str
    subtotal: float
    discount: float
    tax: float
    grand_total: float
    payment_method: Optional[str]
    payment_status: str
    items: List[BillItemResponse] = []
    
    class Config:
        from_attributes = True


# Auth Schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

# Analytics Schemas
class LowStockProduct(BaseModel):
    id: int
    name: str
    sku: str
    quantity_left: int


class TopSellingProduct(BaseModel):
    product_id: int
    product_name: str
    total_quantity_sold: int
    total_revenue: float


class RecentSaleInfo(BaseModel):
    sale_id: int
    product_name: str
    quantity: int
    total_amount: float
    sale_date: datetime


class DashboardResponse(BaseModel):
    total_products: int
    total_sales_count: int
    total_revenue: float
    total_profit: float
    low_stock_products: List[LowStockProduct]
    top_selling_products: List[TopSellingProduct]
    recent_sales: List[RecentSaleInfo]