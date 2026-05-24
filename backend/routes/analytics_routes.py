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
from utils.auth import get_current_active_user  # ← Add this import

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Add this
):
    # Get all metrics
    total_products = analytics_crud.get_total_products_count(db)
    total_sales_count = analytics_crud.get_total_sales_count(db)
    total_revenue = analytics_crud.get_total_revenue(db)
    total_profit = analytics_crud.get_total_profit(db)
    
    low_stock_products_data = analytics_crud.get_low_stock_products(db)
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
    
    top_selling_data = analytics_crud.get_top_selling_products(db)
    top_selling_products = []
    for item in top_selling_data:
        top_selling_products.append(
            TopSellingProduct(
                product_id=item.product_id,
                product_name=item.product_name,
                total_quantity_sold=item.total_quantity_sold,
                total_revenue=float(item.total_revenue)
            )
        )
    
    recent_sales_data = analytics_crud.get_recent_sales(db)
    recent_sales = []
    for sale in recent_sales_data:
        recent_sales.append(
            RecentSaleInfo(
                sale_id=sale.sale_id,
                product_name=sale.product_name,
                quantity=sale.quantity,
                total_amount=float(sale.total_amount),
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