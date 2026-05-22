from sqlalchemy.orm import Session
from models import Sale, Product
from schemas import SaleCreate
from crud import product_crud


def create_sale(db: Session, sale: SaleCreate):

    product = product_crud.get_product_by_id(db, sale.product_id)
    
   
    if product is None:
        return None
    
   
    if product.quantity_left < sale.quantity:
        return "not_enough_stock"
    
    selling_price_at_time = product.selling_price
    cost_price_at_time = product.cost_price
    total_amount = selling_price_at_time * sale.quantity
    profit = (selling_price_at_time - cost_price_at_time) * sale.quantity
    
    db_sale = Sale(
        product_id=sale.product_id,
        quantity=sale.quantity,
        selling_price_at_time=selling_price_at_time,
        cost_price_at_time=cost_price_at_time,
        total_amount=total_amount,
        profit=profit,
        customer_name=sale.customer_name
    )
    

    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    

    product_crud.decrease_stock(db, sale.product_id, sale.quantity)
    
    return db_sale


def get_all_sales(db: Session):
    return db.query(Sale).order_by(Sale.sale_date.desc()).all()


def get_sale_by_id(db: Session, sale_id: int):
    return db.query(Sale).filter(Sale.id == sale_id).first()


def get_sales_by_product(db: Session, product_id: int):
    return db.query(Sale).filter(Sale.product_id == product_id).order_by(Sale.sale_date.desc()).all()
