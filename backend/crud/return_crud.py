from sqlalchemy.orm import Session
from models import Return, Sale, Product
from schemas import ReturnCreate
from crud import product_crud


def create_return(db: Session, return_data: ReturnCreate):
   
    sale = db.query(Sale).filter(Sale.id == return_data.sale_id).first()
    if not sale:
        return "sale_not_found"
   
    if sale.product_id != return_data.product_id:
        return "product_mismatch"
    
    if return_data.quantity > sale.quantity:
        return "quantity_exceeds_sale"
    
    
    refund_amount = sale.selling_price_at_time * return_data.quantity
    
  
    new_return = Return(
        sale_id=return_data.sale_id,
        product_id=return_data.product_id,
        quantity=return_data.quantity,
        reason=return_data.reason,
        refund_amount=refund_amount
    )
    
    db.add(new_return)
    db.commit()
    db.refresh(new_return)
  
    product_crud.increase_stock(db, return_data.product_id, return_data.quantity)
    
    return new_return


def get_all_returns(db: Session):
    return db.query(Return).order_by(Return.return_date.desc()).all()


def get_return_by_id(db: Session, return_id: int):
    return db.query(Return).filter(Return.id == return_id).first()


def get_returns_by_sale(db: Session, sale_id: int):
    return db.query(Return).filter(Return.sale_id == sale_id).order_by(Return.return_date.desc()).all()