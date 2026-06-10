from sqlalchemy.orm import Session
from models import Sale, Product
from schemas import SaleCreate
from crud import product_crud


def create_sale(db: Session, sale: SaleCreate, user_id: int):
    """Create a sale record with user isolation"""
    
    # ← FIXED: Pass user_id to the updated product_crud function
    product = product_crud.get_product_by_id(db, sale.product_id, user_id)
    
    if product is None:
        return None
    
    if product.quantity_left < sale.quantity:
        return "not_enough_stock"
    
    selling_price_at_time = product.selling_price
    cost_price_at_time = product.cost_price
    total_amount = selling_price_at_time * sale.quantity
    profit = (selling_price_at_time - cost_price_at_time) * sale.quantity
    
    # ← FIXED: Removed manual ID calculation so database auto-increments
    db_sale = Sale(
        product_id=sale.product_id,
        quantity=sale.quantity,
        selling_price_at_time=selling_price_at_time,
        cost_price_at_time=cost_price_at_time,
        total_amount=total_amount,
        profit=profit,
        customer_name=sale.customer_name,
        user_id=user_id  
    )
    
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    
    # ← FIXED: Pass user_id to decrease_stock
    product_crud.decrease_stock(db, sale.product_id, sale.quantity, user_id)
    
    return db_sale


def get_all_sales(db: Session, user_id: int):
    """Get all sales for a specific user"""
    return db.query(Sale).filter(Sale.user_id == user_id).order_by(Sale.sale_date.desc()).all()


def get_sale_by_id(db: Session, sale_id: int, user_id: int):
    """Get a specific sale (with user validation)"""
    return db.query(Sale).filter(Sale.id == sale_id, Sale.user_id == user_id).first()


def get_sales_by_product(db: Session, product_id: int, user_id: int):
    """Get sales for a product (filtered by user)"""
    return db.query(Sale).filter(
        Sale.product_id == product_id,
        Sale.user_id == user_id
    ).order_by(Sale.sale_date.desc()).all()


def get_sales_by_date_range(db: Session, user_id: int, start_date, end_date):
    """Get sales within a date range for a user"""
    return db.query(Sale).filter(
        Sale.user_id == user_id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).order_by(Sale.sale_date.desc()).all()