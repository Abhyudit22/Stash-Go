from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import sale_crud
from schemas import SaleCreate, SaleResponse

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/", response_model=SaleResponse)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    result = sale_crud.create_sale(db, sale)
    
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if result == "not_enough_stock":
        raise HTTPException(status_code=400, detail="Not enough stock available")
    
    # Manual conversion for response
    return {
        "id": result.id,
        "product_id": result.product_id,
        "product_name": result.product.name,
        "quantity": result.quantity,
        "selling_price_at_time": result.selling_price_at_time,
        "cost_price_at_time": result.cost_price_at_time,
        "total_amount": result.total_amount,
        "profit": result.profit,
        "customer_name": result.customer_name,
        "sale_date": result.sale_date
    }


@router.get("/", response_model=list[SaleResponse])
def get_all_sales(db: Session = Depends(get_db)):
    sales = sale_crud.get_all_sales(db)
    
    result = []
    for sale in sales:
        result.append({
            "id": sale.id,
            "product_id": sale.product_id,
            "product_name": sale.product.name,
            "quantity": sale.quantity,
            "selling_price_at_time": sale.selling_price_at_time,
            "cost_price_at_time": sale.cost_price_at_time,
            "total_amount": sale.total_amount,
            "profit": sale.profit,
            "customer_name": sale.customer_name,
            "sale_date": sale.sale_date
        })
    
    return result


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale_by_id(sale_id: int, db: Session = Depends(get_db)):
    sale = sale_crud.get_sale_by_id(db, sale_id)
    
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    return {
        "id": sale.id,
        "product_id": sale.product_id,
        "product_name": sale.product.name,
        "quantity": sale.quantity,
        "selling_price_at_time": sale.selling_price_at_time,
        "cost_price_at_time": sale.cost_price_at_time,
        "total_amount": sale.total_amount,
        "profit": sale.profit,
        "customer_name": sale.customer_name,
        "sale_date": sale.sale_date
    }


@router.get("/product/{product_id}", response_model=list[SaleResponse])
def get_sales_by_product(product_id: int, db: Session = Depends(get_db)):
    sales = sale_crud.get_sales_by_product(db, product_id)
    
    result = []
    for sale in sales:
        result.append({
            "id": sale.id,
            "product_id": sale.product_id,
            "product_name": sale.product.name,
            "quantity": sale.quantity,
            "selling_price_at_time": sale.selling_price_at_time,
            "cost_price_at_time": sale.cost_price_at_time,
            "total_amount": sale.total_amount,
            "profit": sale.profit,
            "customer_name": sale.customer_name,
            "sale_date": sale.sale_date
        })
    
    return result