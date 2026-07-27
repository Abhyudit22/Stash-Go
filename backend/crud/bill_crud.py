from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import Bill, BillItem, Product, Sale
from crud import product_crud
from schemas import BillCreate, BillItemCreate, BillUpdate
import models

def generate_bill_number(db: Session):
    """Generate unique bill number: BILL-20250525-0001"""
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(Bill).filter(Bill.bill_number.like(f"BILL-{today}-%")).count()
    return f"BILL-{today}-{count + 1:04d}"

def calculate_totals(bill: Bill):
    """Recalculate subtotal and grand total"""
    subtotal = sum(item.total_price for item in bill.items)
    discount_amt = bill.discount or 0.0
    tax_amt = bill.tax or 0.0
    grand_total = max(0.0, subtotal - discount_amt + tax_amt)
    return round(subtotal, 2), round(grand_total, 2)

def create_bill(db: Session, bill_data: BillCreate, user_id: int):
    """Create a new draft bill - with user isolation"""
    bill_number = generate_bill_number(db)
    
    db_bill = Bill(
        bill_number=bill_number,
        customer_name=bill_data.customer_name,
        customer_phone=bill_data.customer_phone,
        customer_email=bill_data.customer_email,
        status="draft",
        subtotal=0,
        discount=0,
        tax=0,
        grand_total=0,
        payment_status="pending",
        user_id=user_id
    )
    
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    
    return db_bill

def add_item_to_bill(db: Session, bill_id: int, item_data: BillItemCreate, user_id: int):
    """Add item to draft bill - with user validation"""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    
    if not bill or bill.user_id != user_id:
        return "bill_not_found"
    
    if bill.status != "draft":
        return "bill_not_draft"
    
    product = product_crud.get_product_by_id(db, item_data.product_id, user_id)
    if not product:
        return "product_not_found"
    
    existing_item = db.query(BillItem).filter(
        BillItem.bill_id == bill_id,
        BillItem.product_id == item_data.product_id
    ).first()
    
    if existing_item:
        new_quantity = existing_item.quantity + item_data.quantity
        if product.quantity_left < new_quantity:
            return "insufficient_stock"
        existing_item.quantity = new_quantity
        existing_item.total_price = existing_item.quantity * product.selling_price
        target_item = existing_item
    else:
        if product.quantity_left < item_data.quantity:
            return "insufficient_stock"
        
        item_total = product.selling_price * item_data.quantity
        bill_item = BillItem(
            bill_id=bill_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=product.selling_price,
            total_price=item_total
        )
        db.add(bill_item)
        target_item = bill_item
    
    db.flush()
    db.refresh(bill)
    bill.subtotal, bill.grand_total = calculate_totals(bill)
    
    db.commit()
    db.refresh(target_item)
    db.refresh(bill)
    
    return target_item

def remove_item_from_bill(db: Session, bill_id: int, item_id: int, user_id: int):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    
    if not bill or bill.user_id != user_id:
        return "bill_not_found"
    
    if bill.status != "draft":
        return "bill_not_draft"
    
    item = db.query(BillItem).filter(BillItem.id == item_id, BillItem.bill_id == bill_id).first()
    if not item:
        return "item_not_found"
    
    db.delete(item)
    db.flush()
    db.refresh(bill)
    bill.subtotal, bill.grand_total = calculate_totals(bill)
    
    db.commit()
    return "item_removed"

def update_bill_details(db: Session, bill_id: int, bill_update: BillUpdate, user_id: int):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    
    if not bill or bill.user_id != user_id:
        return "bill_not_found"
    
    if bill.status != "draft":
        return "bill_not_draft"
    
    if bill_update.customer_name is not None: bill.customer_name = bill_update.customer_name
    if bill_update.customer_phone is not None: bill.customer_phone = bill_update.customer_phone
    if bill_update.customer_email is not None: bill.customer_email = bill_update.customer_email
    if bill_update.discount is not None: bill.discount = bill_update.discount
    if bill_update.tax is not None: bill.tax = bill_update.tax
    if bill_update.payment_method is not None: bill.payment_method = bill_update.payment_method
    
    db.flush()
    db.refresh(bill)
    bill.subtotal, bill.grand_total = calculate_totals(bill)
    
    db.commit()
    db.refresh(bill)
    return bill

def finalize_bill(db: Session, bill_id: int, user_id: int):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    
    if not bill or bill.user_id != user_id:
        return "bill_not_found"
    
    if bill.status != "draft":
        return "bill_not_draft"
    
    if not bill.items:
        return "bill_empty"
    
    # FIXED: Pass user_id in these stock checks
    for item in bill.items:
        product = product_crud.get_product_by_id(db, item.product_id, user_id)
        if not product or product.quantity_left < item.quantity:
            return f"insufficient_stock_{item.product_id}"
    
    sales_created = []
    
    # FIXED: Pass user_id here as well
    for item in bill.items:
        product = product_crud.get_product_by_id(db, item.product_id, user_id)
        
        sale = Sale(
            product_id=item.product_id,
            quantity=item.quantity,
            selling_price_at_time=item.unit_price,
            cost_price_at_time=product.cost_price,
            total_amount=item.total_price,
            profit=(item.unit_price - product.cost_price) * item.quantity,
            customer_name=bill.customer_name,
            user_id=user_id,
            bill_id=bill.id
        )
        db.add(sale)
        db.flush()
        product.quantity_left -= item.quantity
        
        sales_created.append({"sale_id": sale.id, "product_name": product.name, "quantity": item.quantity})
    
    bill.status = "finalized"
    bill.payment_status = "paid"
    
    db.commit()
    return {"message": "Finalized", "bill_number": bill.bill_number, "sales": sales_created}

def delete_bill(db: Session, bill_id: int, user_id: int):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    
    if not bill or bill.user_id != user_id:
        return "unauthorized"

    # FIXED: Ensure stock update query is filtered by user_id
    if bill.status == "finalized":
        for item in bill.items:
            product = db.query(models.Product).filter(
                models.Product.id == item.product_id, 
                models.Product.user_id == user_id
            ).first()
            if product:
                product.quantity_left += item.quantity 
        db.commit() 
   
    sales = db.query(models.Sale.id).filter(models.Sale.bill_id == bill_id).all()
    sale_ids = [sale.id for sale in sales]

    if sale_ids:
        db.query(models.Return).filter(models.Return.sale_id.in_(sale_ids)).delete(synchronize_session=False)
   
    db.query(models.Sale).filter(models.Sale.bill_id == bill_id).delete(synchronize_session=False)
    db.query(models.BillItem).filter(models.BillItem.bill_id == bill_id).delete(synchronize_session=False)

    db.delete(bill)
    db.commit()
    return "success"
def get_bill(db: Session, bill_id: int, user_id: int):
    """Get bill by ID with items - with user validation"""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    
    if bill and bill.user_id != user_id:
        return None
        
    return bill