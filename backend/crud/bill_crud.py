from datetime import datetime
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
    grand_total = subtotal - bill.discount + bill.tax
    return subtotal, grand_total


def create_bill(db: Session, bill_data: BillCreate):
    """Create a new draft bill (NO sale created yet)"""
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
        payment_status="pending"
    )
    
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    
    return db_bill


def add_item_to_bill(db: Session, bill_id: int, item_data: BillItemCreate):
    """Add item to draft bill"""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        return "bill_not_found"
    
    if bill.status != "draft":
        return "bill_not_draft"
    
    product = product_crud.get_product_by_id(db, item_data.product_id)
    if not product:
        return "product_not_found"
    
    # Check stock availability
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
    
    # Update bill totals
    bill.subtotal, bill.grand_total = calculate_totals(bill)
    
    db.commit()
    db.refresh(bill_item)
    
    return bill_item


def remove_item_from_bill(db: Session, bill_id: int, item_id: int):
    """Remove item from draft bill"""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        return "bill_not_found"
    
    if bill.status != "draft":
        return "bill_not_draft"
    
    item = db.query(BillItem).filter(BillItem.id == item_id, BillItem.bill_id == bill_id).first()
    if not item:
        return "item_not_found"
    
    db.delete(item)
    
    # Update bill totals
    bill.subtotal, bill.grand_total = calculate_totals(bill)
    
    db.commit()
    
    return "item_removed"


def update_bill_details(db: Session, bill_id: int, bill_update: BillUpdate):
    """Update bill details (customer, discount, tax, payment)"""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        return "bill_not_found"
    
    if bill.status != "draft":
        return "bill_not_draft"
    
    if bill_update.customer_name is not None:
        bill.customer_name = bill_update.customer_name
    if bill_update.customer_phone is not None:
        bill.customer_phone = bill_update.customer_phone
    if bill_update.customer_email is not None:
        bill.customer_email = bill_update.customer_email
    if bill_update.discount is not None:
        bill.discount = bill_update.discount
    if bill_update.tax is not None:
        bill.tax = bill_update.tax
    if bill_update.payment_method is not None:
        bill.payment_method = bill_update.payment_method
    
    # Recalculate grand total
    bill.subtotal, bill.grand_total = calculate_totals(bill)
    
    db.commit()
    db.refresh(bill)
    
    return bill


def finalize_bill(db: Session, bill_id: int, user_id: int = None):
    """Finalize bill and create sales records (THIS creates sale and deducts stock)"""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        return "bill_not_found"
    
    if bill.status != "draft":
        return "bill_not_draft"
    
    if not bill.items:
        return "bill_empty"
    
    if not bill.payment_method:
        return "payment_method_required"
    
    # Check stock for all items first
    for item in bill.items:
        product = product_crud.get_product_by_id(db, item.product_id)
        if product.quantity_left < item.quantity:
            return f"insufficient_stock_{item.product_id}"
    
    sales_created = []
    
    # Create sale for each item and deduct stock
    for item in bill.items:
        product = product_crud.get_product_by_id(db, item.product_id)
        
        # Create sale record
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
        db.flush()  # Get sale ID without committing
        
        # Deduct stock
        product.quantity_left -= item.quantity
        
        sales_created.append({
            "sale_id": sale.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "total_amount": item.total_price
        })
    
    # Update bill status
    bill.status = "finalized"
    bill.payment_status = "paid"
    
    db.commit()
    db.refresh(bill)
    
    return {
        "message": "Bill finalized and sales created",
        "bill_id": bill.id,
        "bill_number": bill.bill_number,
        "sales": sales_created
    }


def get_bill(db: Session, bill_id: int):
    """Get bill by ID with items"""
    return db.query(Bill).filter(Bill.id == bill_id).first()


def get_all_bills(db: Session):
    """Get all bills"""
    return db.query(Bill).order_by(Bill.created_date.desc()).all()
def delete_bill(db: Session, bill_id: int):
    # Fetch the bill
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    
    if not bill:
        return "bill_not_found"

    # --- 1. NEW FIX: Delete the linked record in the `sales` table first ---
    db.query(models.Sale).filter(models.Sale.bill_id == bill_id).delete()
    
    # --- 2. Restore stock and delete the line items ---
    if hasattr(bill, 'items'):
        for item in bill.items:
            # Restore the stock
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if product:
                product.quantity_left += item.quantity 
            
            # Delete the item
            db.delete(item)
            
    # --- 3. Now that all children are gone, safely delete the parent bill ---
    db.delete(bill)
    db.commit()
    
    return "success"