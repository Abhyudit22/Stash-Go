from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import analytics_crud
from schemas import (
    DashboardResponse,
    LowStockProduct,
    TopSellingProduct,
    RecentSaleInfo
)
from utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = current_user.id # Capture the logged-in user's ID

    # FIXED: Pass user_id to every CRUD function
    total_products = analytics_crud.get_total_products_count(db, user_id) or 0
    total_sales_count = analytics_crud.get_total_sales_count(db, user_id) or 0
    total_revenue = analytics_crud.get_total_revenue(db, user_id) or 0.0
    total_profit = analytics_crud.get_total_profit(db, user_id) or 0.0
    
    # FIXED: Pass user_id here as well
    low_stock_products_data = analytics_crud.get_low_stock_products(db, user_id) or []
    low_stock_products = []
    for product in low_stock_products_data:
        low_stock_products.append(
            LowStockProduct(
                id=product.id,
                name=product.name,
                sku=product.sku,
                quantity_left=product.quantity_left
            )
        )
    
    # FIXED: Pass user_id here as well
    top_selling_data = analytics_crud.get_top_selling_products(db, user_id) or []
    top_selling_products = []
    for item in top_selling_data:
        rev_val = item.total_revenue if item.total_revenue is not None else 0.0
        top_selling_products.append(
            TopSellingProduct(
                product_id=item.product_id,
                product_name=item.product_name,
                total_quantity_sold=item.total_quantity_sold or 0,
                total_revenue=float(rev_val)
            )
        )
    
    # FIXED: Pass user_id here as well
    recent_sales_data = analytics_crud.get_recent_sales(db, user_id) or []
    recent_sales = []
    for sale in recent_sales_data:
        amt_val = sale.total_amount if sale.total_amount is not None else 0.0
        recent_sales.append(
            RecentSaleInfo(
                sale_id=sale.sale_id,
                product_name=sale.product_name,
                quantity=sale.quantity or 0,
                total_amount=float(amt_val),
                sale_date=sale.sale_date
            )
        )
    
    return DashboardResponse(
        total_products=total_products,
        total_sales_count=total_sales_count,
        total_revenue=total_revenue,
        total_profit=total_profit,
        low_stock_products=low_stock_products,
        top_selling_products=top_selling_products,
        recent_sales=recent_sales
    )