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

    total_products = analytics_crud.get_total_products_count(db) or 0
    total_sales_count = analytics_crud.get_total_sales_count(db) or 0
    total_revenue = analytics_crud.get_total_revenue(db) or 0.0
    total_profit = analytics_crud.get_total_profit(db) or 0.0
    
    low_stock_products_data = analytics_crud.get_low_stock_products(db) or []
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
    
    top_selling_data = analytics_crud.get_top_selling_products(db) or []
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
    
    # 4. Process Recent Sales safely
    recent_sales_data = analytics_crud.get_recent_sales(db) or []
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
    
    # Return clean values to clear the frontend infinite loading screen
    return DashboardResponse(
        total_products=total_products,
        total_sales_count=total_sales_count,
        total_revenue=total_revenue,
        total_profit=total_profit,
        low_stock_products=low_stock_products,
        top_selling_products=top_selling_products,
        recent_sales=recent_sales
    )