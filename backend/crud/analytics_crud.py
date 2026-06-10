from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import Product, Sale

def get_total_products_count(db: Session, user_id: int):
  
    return db.query(Product).filter(Product.user_id == user_id).count()

def get_total_sales_count(db: Session, user_id: int):
    
    return db.query(Sale).filter(Sale.user_id == user_id).count()

def get_total_revenue(db: Session, user_id: int):
    
    result = db.query(func.sum(Sale.total_amount)).filter(Sale.user_id == user_id).first()
    return float(result[0]) if result[0] is not None else 0.0

def get_total_profit(db: Session, user_id: int):
  
    result = db.query(func.sum(Sale.profit)).filter(Sale.user_id == user_id).first()
    return float(result[0]) if result[0] is not None else 0.0

def get_low_stock_products(db: Session, user_id: int, threshold: int = 10):
    
    return db.query(Product).filter(
        Product.user_id == user_id,
        Product.quantity_left < threshold
    ).order_by(Product.quantity_left.asc()).all()

def get_top_selling_products(db: Session, user_id: int, limit: int = 5):
   
    results = db.query(
        Sale.product_id,
        Product.name.label("product_name"),
        func.sum(Sale.quantity).label("total_quantity_sold"),
        func.sum(Sale.total_amount).label("total_revenue")
    ).join(Product, Sale.product_id == Product.id) \
     .filter(Sale.user_id == user_id) \
     .group_by(Sale.product_id, Product.name) \
     .order_by(desc("total_quantity_sold")) \
     .limit(limit) \
     .all()
    
    return results

def get_recent_sales(db: Session, user_id: int, limit: int = 5):
    
    results = db.query(
        Sale.id.label("sale_id"),
        Product.name.label("product_name"),
        Sale.quantity,
        Sale.total_amount,
        Sale.sale_date
    ).join(Product, Sale.product_id == Product.id) \
     .filter(Sale.user_id == user_id) \
     .order_by(desc(Sale.sale_date)) \
     .limit(limit) \
     .all()
    
    return results