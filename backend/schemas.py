from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from pydantic import Field
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field



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
    quantity: int
    selling_price_at_time: float
    cost_price_at_time: float
    total_amount: float
    profit: float
    customer_name: Optional[str]
    sale_date: datetime
    
    class Config:
        from_attributes = True

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

class Billingitems(BaseModel):
    # product_name : str
    quantity : int
    unit_price : int
    total_price: int
class BillingResponse(BaseModel):
    
    bill_number: str
    bill_date: datetime
    customer_name: Optional[str]
    items: List
    subtotal: float
    discount: float
    tax: float
    grand_total: float
    payment_method: str
    payment_status: str

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