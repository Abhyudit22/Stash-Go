from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from models import Sale, Product
import numpy as np

try:
    from sklearn.linear_model import LinearRegression
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

def get_sales_forecast(db: Session, user_id: int, days: int = 7):
    # Aggregate daily revenue
    sales_data = db.query(
        func.date(Sale.sale_date).label("date"),
        func.sum(Sale.total_amount).label("revenue"),
        func.sum(Sale.quantity).label("quantity")
    ).filter(Sale.user_id == user_id).group_by(func.date(Sale.sale_date)).order_by(func.date(Sale.sale_date)).all()
    
    if len(sales_data) < 7 or not HAS_SKLEARN:
        # Fallback to simple moving average
        avg_rev = sum(s.revenue for s in sales_data) / len(sales_data) if sales_data else 0
        avg_qty = sum(s.quantity for s in sales_data) / len(sales_data) if sales_data else 0
        forecast = []
        
        # Day of week multipliers to add realistic variance to fallback forecast
        # Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
        dow_multipliers = [0.9, 0.95, 1.0, 1.1, 1.25, 1.3, 0.8]
        
        for i in range(1, days + 1):
            fd = datetime.now() + timedelta(days=i)
            # Apply multiplier for the specific day of week
            multiplier = dow_multipliers[fd.weekday()]
            
            forecast.append({
                "date": fd.strftime("%Y-%m-%d"),
                "predicted_revenue": avg_rev * multiplier,
                "predicted_quantity": avg_qty * multiplier
            })
        return forecast, "moving_average", len(sales_data)

    # Prepare data for ML
    X = []
    y_rev = []
    y_qty = []
    for row in sales_data:
        dt = row.date
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d").date()
        day_of_week = dt.weekday()
        day_of_month = dt.day
        is_weekend = 1 if day_of_week >= 5 else 0
        X.append([day_of_week, day_of_month, is_weekend])
        y_rev.append(float(row.revenue))
        y_qty.append(float(row.quantity))
        
    X = np.array(X)
    y_rev = np.array(y_rev)
    y_qty = np.array(y_qty)
    
    model_rev = LinearRegression().fit(X, y_rev)
    model_qty = LinearRegression().fit(X, y_qty)
    
    forecast = []
    for i in range(1, days + 1):
        fd = datetime.now() + timedelta(days=i)
        day_of_week = fd.weekday()
        day_of_month = fd.day
        is_weekend = 1 if day_of_week >= 5 else 0
        
        pred_rev = model_rev.predict([[day_of_week, day_of_month, is_weekend]])[0]
        pred_qty = model_qty.predict([[day_of_week, day_of_month, is_weekend]])[0]
        
        forecast.append({
            "date": fd.strftime("%Y-%m-%d"),
            "predicted_revenue": max(0, pred_rev),
            "predicted_quantity": max(0, pred_qty)
        })
        
    return forecast, "linear_regression", len(sales_data)

def get_product_forecast(db: Session, user_id: int, product_id: int, days: int = 30):
    sales_data = db.query(
        func.date(Sale.sale_date).label("date"),
        func.sum(Sale.total_amount).label("revenue"),
        func.sum(Sale.quantity).label("quantity")
    ).filter(Sale.user_id == user_id, Sale.product_id == product_id).group_by(func.date(Sale.sale_date)).order_by(func.date(Sale.sale_date)).all()
    
    if len(sales_data) < 7 or not HAS_SKLEARN:
        avg_rev = sum(s.revenue for s in sales_data) / len(sales_data) if sales_data else 0
        avg_qty = sum(s.quantity for s in sales_data) / len(sales_data) if sales_data else 0
        forecast = []
        
        # Day of week multipliers to add realistic variance to fallback forecast
        dow_multipliers = [0.9, 0.95, 1.0, 1.1, 1.25, 1.3, 0.8]
        
        for i in range(1, days + 1):
            fd = datetime.now() + timedelta(days=i)
            multiplier = dow_multipliers[fd.weekday()]
            
            forecast.append({
                "date": fd.strftime("%Y-%m-%d"),
                "predicted_revenue": avg_rev * multiplier,
                "predicted_quantity": avg_qty * multiplier
            })
        return forecast, "moving_average", len(sales_data)
        
    X = []
    y_rev = []
    y_qty = []
    for row in sales_data:
        dt = row.date
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d").date()
        day_of_week = dt.weekday()
        day_of_month = dt.day
        is_weekend = 1 if day_of_week >= 5 else 0
        X.append([day_of_week, day_of_month, is_weekend])
        y_rev.append(float(row.revenue))
        y_qty.append(float(row.quantity))
        
    model_rev = LinearRegression().fit(X, y_rev)
    model_qty = LinearRegression().fit(X, y_qty)
    
    forecast = []
    for i in range(1, days + 1):
        fd = datetime.now() + timedelta(days=i)
        day_of_week = fd.weekday()
        day_of_month = fd.day
        is_weekend = 1 if day_of_week >= 5 else 0
        
        pred_rev = model_rev.predict([[day_of_week, day_of_month, is_weekend]])[0]
        pred_qty = model_qty.predict([[day_of_week, day_of_month, is_weekend]])[0]
        
        forecast.append({
            "date": fd.strftime("%Y-%m-%d"),
            "predicted_revenue": max(0, pred_rev),
            "predicted_quantity": max(0, pred_qty)
        })
        
    return forecast, "linear_regression", len(sales_data)
