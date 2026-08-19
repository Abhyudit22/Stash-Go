from sqlalchemy.orm import Session
from models import Bill, BillItem, Product
from collections import Counter

def get_recommendations(db: Session, user_id: int, product_id: int, limit: int = 5):
    # Find all bill IDs where this product was purchased
    target_bills = db.query(BillItem.bill_id).join(Bill).filter(
        Bill.user_id == user_id,
        BillItem.product_id == product_id
    ).all()
    
    if not target_bills:
        return []
        
    bill_ids = [b.bill_id for b in target_bills]
    
    # Get all items in these bills
    all_items = db.query(BillItem.product_id, Product.name, Product.sku, Product.selling_price).join(Product, BillItem.product_id == Product.id).filter(
        BillItem.bill_id.in_(bill_ids),
        BillItem.product_id != product_id
    ).all()
    
    co_purchases = Counter([item.product_id for item in all_items])
    
    # Create product info dict
    product_info = {item.product_id: item for item in all_items}
    
    results = []
    for pid, count in co_purchases.most_common(limit):
        info = product_info[pid]
        results.append({
            "product_id": pid,
            "product_name": info.name,
            "sku": info.sku,
            "selling_price": info.selling_price,
            "co_purchase_count": count,
            "confidence": count / len(bill_ids)
        })
        
    return results
