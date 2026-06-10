from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    # REMOVED unique=True so different users can use the same SKU
    sku = Column(String, index=True, nullable=False) 
    name = Column(String, nullable=False)
    cost_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    quantity_left = Column(Integer, nullable=False)
    
    # NEW: Isolate inventory per user
    user_id = Column(Integer, ForeignKey("user_auth.id"), nullable=False) 
    
    # NEW: Ensure SKU is unique only WITHIN a specific user's account
    __table_args__ = (UniqueConstraint('sku', 'user_id', name='_user_sku_uc'),)
    
    # Relationships configured with cascading deletes
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")
    returns = relationship("Return", back_populates="product", cascade="all, delete-orphan")
    bill_items = relationship("BillItem", back_populates="product", cascade="all, delete-orphan")
    user = relationship("User_Auth", back_populates="products") # NEW


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    selling_price_at_time = Column(Float, nullable=False)
    cost_price_at_time = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    customer_name = Column(String, nullable=True)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("user_auth.id"), nullable=False)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="sales")
    returns = relationship("Return", back_populates="sale")
    bill = relationship("Bill", back_populates="sale")
    user = relationship("User_Auth", back_populates="sales")


class Return(Base):
    __tablename__ = "returns"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    refund_amount = Column(Float, nullable=False)
    return_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # NEW: Isolate returns per user
    user_id = Column(Integer, ForeignKey("user_auth.id"), nullable=False)
    
    # Relationships
    sale = relationship("Sale", back_populates="returns")
    product = relationship("Product", back_populates="returns")
    user = relationship("User_Auth", back_populates="returns") # NEW
    
    @property
    def product_name(self):
        return self.product.name


class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_number = Column(String, unique=True, index=True)
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="draft")
    subtotal = Column(Float, default=0)
    discount = Column(Float, default=0)
    tax = Column(Float, default=0)
    grand_total = Column(Float, default=0)
    payment_method = Column(String, nullable=True)
    payment_status = Column(String, default="pending")
    user_id = Column(Integer, ForeignKey("user_auth.id"), nullable=False)
    
    # Relationships
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")
    sale = relationship("Sale", back_populates="bill", uselist=False)
    user = relationship("User_Auth", back_populates="bills")


class BillItem(Base):
    __tablename__ = "bill_items"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    bill = relationship("Bill", back_populates="items")
    product = relationship("Product")
    
    @property
    def product_name(self):
        return self.product.name if self.product else "Unknown Product"

    @property
    def sku(self):
        return self.product.sku if self.product else "N/A"

class User_Auth(Base):
    __tablename__ = "user_auth"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships to user's data
    sales = relationship("Sale", back_populates="user", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="user", cascade="all, delete-orphan") # NEW
    returns = relationship("Return", back_populates="user", cascade="all, delete-orphan") # NEW