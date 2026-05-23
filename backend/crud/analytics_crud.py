from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import Product, Sale


def get_total_products_count(db: Session):
    
    return db.query(Product).count()


def get_total_sales_count(db: Session):
    
    return db.query(Sale).count()


def get_total_revenue(db: Session):
    
    result = db.query(func.sum(Sale.total_amount)).first()
    # result[0] is the sum value, or None if no sales exist
    if result[0] is None:
        return 0.0
    return float(result[0])


def get_total_profit(db: Session):
    
    result = db.query(func.sum(Sale.profit)).first()
    if result[0] is None:
        return 0.0
    return float(result[0])


def get_low_stock_products(db: Session, threshold: int = 10):
    
    products = db.query(Product).filter(Product.quantity_left < threshold).order_by(Product.quantity_left.asc()).all()
    return products


def get_top_selling_products(db: Session, limit: int = 5):
    
    results = db.query(
        Sale.product_id,
        Product.name.label("product_name"),
        func.sum(Sale.quantity).label("total_quantity_sold"),
        func.sum(Sale.total_amount).label("total_revenue")
    ).join(Product, Sale.product_id == Product.id) \
     .group_by(Sale.product_id, Product.name) \
     .order_by(desc("total_quantity_sold")) \
     .limit(limit) \
     .all()
    
    return results


def get_recent_sales(db: Session, limit: int = 5):
    
    results = db.query(
        Sale.id.label("sale_id"),
        Product.name.label("product_name"),
        Sale.quantity,
        Sale.total_amount,
        Sale.sale_date
    ).join(Product, Sale.product_id == Product.id) \
     .order_by(desc(Sale.sale_date)) \
     .limit(limit) \
     .all()
    
    return results