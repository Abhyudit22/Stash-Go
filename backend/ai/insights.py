from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from models import Product, Sale

def get_smart_restock_alerts(db: Session, user_id: int):
    # For each product, calculate avg_daily_sales from Sale table
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    sales_data = db.query(
        Sale.product_id,
        func.sum(Sale.quantity).label("total_quantity")
    ).filter(
        Sale.user_id == user_id,
        Sale.sale_date >= thirty_days_ago
    ).group_by(Sale.product_id).all()
    
    sales_dict = {item.product_id: item.total_quantity for item in sales_data}
    products = db.query(Product).filter(Product.user_id == user_id).all()
    
    alerts = []
    for p in products:
        total_q = sales_dict.get(p.id, 0)
        avg_daily_sales = total_q / 30.0 if total_q > 0 else 0
        if avg_daily_sales > 0:
            days_until_stockout = p.quantity_left / avg_daily_sales
        else:
            days_until_stockout = float('inf')
            
        urgency = "healthy"
        severity = "info"
        if days_until_stockout < 3:
            urgency = "critical"
            severity = "critical"
        elif days_until_stockout < 7:
            urgency = "warning"
            severity = "warning"
            
        if urgency != "healthy":
            alerts.append({
                "type": "warning",
                "title": f"Restock Alert: {p.name}",
                "description": f"Estimated stockout in {int(days_until_stockout)} days.",
                "severity": severity,
                "metric_value": days_until_stockout
            })
            
    return alerts

def get_anomaly_insights(db: Session, user_id: int):
    # Compare today's sales vs 30-day rolling average
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    sales_data = db.query(
        Sale.product_id,
        func.date(Sale.sale_date).label("date"),
        func.sum(Sale.quantity).label("daily_qty")
    ).filter(
        Sale.user_id == user_id,
        Sale.sale_date >= thirty_days_ago
    ).group_by(Sale.product_id, func.date(Sale.sale_date)).all()
    
    product_sales = {}
    for row in sales_data:
        pid = row.product_id
        if pid not in product_sales:
            product_sales[pid] = []
        product_sales[pid].append({"date": row.date, "qty": row.daily_qty})
        
    products = db.query(Product).filter(Product.user_id == user_id).all()
    p_dict = {p.id: p.name for p in products}
    
    anomalies = []
    import math
    for pid, sales in product_sales.items():
        if len(sales) < 5:
            continue
        
        qtys = [s["qty"] for s in sales if s["date"] != today]
        if not qtys:
            continue
            
        mean = sum(qtys) / len(qtys)
        variance = sum((x - mean) ** 2 for x in qtys) / len(qtys)
        std_dev = math.sqrt(variance)
        
        today_qty = sum(s["qty"] for s in sales if s["date"] == today)
        
        if std_dev > 0:
            z_score = (today_qty - mean) / std_dev
            if abs(z_score) > 2:
                status = "surge" if z_score > 0 else "drop"
                severity = "info" if z_score > 0 else "warning"
                anomalies.append({
                    "type": "anomaly",
                    "title": f"Sales Anomaly: {p_dict.get(pid, 'Unknown')}",
                    "description": f"Unusual {status} in sales today compared to past 30 days.",
                    "severity": severity,
                    "metric_value": z_score
                })
                
    return anomalies

def get_trend_insights(db: Session, user_id: int):
    # Week over week
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)
    
    this_week_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.user_id == user_id, Sale.sale_date >= one_week_ago
    ).scalar() or 0
    
    last_week_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.user_id == user_id, Sale.sale_date >= two_weeks_ago, Sale.sale_date < one_week_ago
    ).scalar() or 0
    
    insights = []
    if last_week_sales > 0:
        pct_change = ((this_week_sales - last_week_sales) / last_week_sales) * 100
        severity = "info" if pct_change >= 0 else "warning"
        direction = "Up" if pct_change >= 0 else "Down"
        insights.append({
            "type": "trend",
            "title": f"Revenue Trend {direction}",
            "description": f"Revenue is {direction.lower()} {abs(pct_change):.1f}% compared to last week.",
            "severity": severity,
            "metric_value": pct_change
        })
    return insights

def get_all_insights(db: Session, user_id: int):
    insights = []
    insights.extend(get_smart_restock_alerts(db, user_id))
    insights.extend(get_anomaly_insights(db, user_id))
    insights.extend(get_trend_insights(db, user_id))
    return insights
