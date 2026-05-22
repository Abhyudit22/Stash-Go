from sqlalchemy import Column , Integer , String , Numeric,Boolean, ForeignKey,Float,DateTime
from database  import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True , index=True)

    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    
    cost_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
  
    quantity_left = Column(Integer, default=0, nullable=False)
    sales = relationship("Sale", back_populates="product")

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
    
    # Relationship
    product = relationship("Product", back_populates="sales")
