from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from models import Product, Sale
from .forecasting import get_sales_forecast

def process_chat_query(question: str, db: Session, user_id: int):
    q = question.lower()
    
    if any(kw in q for kw in ["top product", "top selling", "best seller", "best selling"]):
        intent = "top_products"
        sales = db.query(
            Sale.product_id, Product.name, func.sum(Sale.quantity).label("total")
        ).join(Product).filter(Sale.user_id == user_id).group_by(Sale.product_id, Product.name).order_by(func.sum(Sale.quantity).desc()).limit(5).all()
        data = [{"name": s.name, "quantity": s.total} for s in sales]
        answer = "Here are your top products based on quantity sold."
        
    elif any(kw in q for kw in ["revenue", "total sales"]):
        intent = "revenue"
        total = db.query(func.sum(Sale.total_amount)).filter(Sale.user_id == user_id).scalar() or 0
        data = {"revenue": total}
        answer = f"Your total revenue is ${total:.2f}."
        
    elif any(kw in q for kw in ["profit"]):
        intent = "profit"
        total = db.query(func.sum(Sale.profit)).filter(Sale.user_id == user_id).scalar() or 0
        data = {"profit": total}
        answer = f"Your total profit is ${total:.2f}."
        
    elif any(kw in q for kw in ["low stock", "out of stock", "running out"]):
        intent = "low_stock"
        products = db.query(Product).filter(Product.user_id == user_id, Product.quantity_left < 10).all()
        data = [{"name": p.name, "quantity_left": p.quantity_left} for p in products]
        answer = f"You have {len(products)} items running low in stock."
        
    elif any(kw in q for kw in ["recent sale", "last sale"]):
        intent = "recent_sales"
        sales = db.query(Sale).filter(Sale.user_id == user_id).order_by(Sale.sale_date.desc()).limit(5).all()
        data = [{"date": s.sale_date, "amount": s.total_amount} for s in sales]
        answer = "Here are your most recent sales."
        
    elif "forecast" in q or "predict" in q:
        intent = "forecast"
        forecast, model, pts = get_sales_forecast(db, user_id, days=7)
        data = {"forecast": forecast}
        answer = "Here is the sales forecast for the next 7 days."
        
    elif "product" in q or "info" in q:
        intent = "product_info"
        products = db.query(Product).filter(Product.user_id == user_id).limit(5).all()
        data = [{"name": p.name, "price": p.selling_price} for p in products]
        answer = "Here are some of your products. Please specify a name for better search."
        
    else:
        intent = "unknown"
        data = {}
        answer = "I can help with: top products, revenue, profit, low stock, recent sales, forecasts, and product lookups."
        
    return {"answer": answer, "data": data, "intent": intent}
