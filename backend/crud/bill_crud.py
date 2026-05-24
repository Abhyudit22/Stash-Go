from datetime import datetime
from sqlalchemy.orm import Session
from models import Product, Sale
from crud import product_crud
from schemas import SaleCreate
from routes.sale_routes import create_sale as create_sale_func

def create_bill_and_sale(db: Session, items_list: list, customer_name: str = None, payment_method: str = "cash"):


    bill_items = []
    subtotal = 0
    sales_created = []
    
    
    for item in items_list:
        product = product_crud.get_product_by_id(db, item["product_id"])
        
        if not product:
            return {"error": f"Product {item['product_id']} not found"}
      
        if product.quantity_left < item["quantity"]:
            return {"error": f"Insufficient stock for {product.name}"}

        item_total = product.selling_price * item["quantity"]
        subtotal += item_total
        
       
        bill_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item["quantity"],
            "unit_price": product.selling_price,
            "total_price": item_total
        })
        
        sale_data = SaleCreate(
            product_id=item["product_id"],
            quantity=item["quantity"],
            customer_name=customer_name
        )
        
  
        sale = Sale(
            product_id=item["product_id"],
            quantity=item["quantity"],
            selling_price_at_time=product.selling_price,
            cost_price_at_time=product.cost_price,
            total_amount=item_total,
            profit=(product.selling_price - product.cost_price) * item["quantity"],
            customer_name=customer_name
        )
        
        db.add(sale)
        
  
        product.quantity_left -= item["quantity"]
        
        sales_created.append({
            "sale_id": sale.id,
            "product_name": product.name,
            "quantity": item["quantity"],
            "total_amount": item_total
        })

    discount = 0
    tax = 0
    grand_total = subtotal - discount + tax
    
    bill_number = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db.commit()
    
    
    return {
        "bill_number": bill_number,
        "bill_date": datetime.now(),
        "customer_name": customer_name,
        "items": bill_items,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "grand_total": grand_total,
        "payment_method": payment_method,
        "payment_status": "paid",
        "sales": sales_created
    }