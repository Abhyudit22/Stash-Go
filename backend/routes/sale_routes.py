from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import sale_crud
from schemas import SaleCreate, SaleResponse
from utils.auth import get_current_active_user  # ← Add this import
from sqlalchemy.orm import joinedload
import models

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/", response_model=SaleResponse)
def create_sale(
    sale: SaleCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Add this
):
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


@router.get("/all", response_model=list[SaleResponse])
def get_all_sales(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Add this
):
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
def get_sale_by_id(
    sale_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Add this
):
    sale = sale_crud.get_sale_by_id(db, sale_id)
    
    # Fix: Remove the comma at the end of the line above
    # sale = sale_crud.get_sale_by_id(db, sale_id)  ← No comma
    
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
def get_sales_by_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Add this
):
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
@router.get("", response_model=list[dict])
@router.get("/", response_model=list[dict])
def get_sales_ledger(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    records = db.query(models.BillItem)\
                .options(joinedload(models.BillItem.product))\
                .options(joinedload(models.BillItem.bill))\
                .all()
    
    result = []
    for item in records:
        result.append({
            "id": item.bill_id,
            "bill_id": item.bill_id,
            "product_id": item.product_id,
            "product_name": item.product.name if item.product else f"Product #{item.product_id}",
            "sku": item.product.sku if item.product else "N/A",
            "quantity": item.quantity,
            "selling_price": item.product.selling_price if item.product else 0.0,
            "cost_price": item.product.cost_price if item.product else 0.0,
            "customer_name": item.bill.customer_name if item.bill else "Walk-in Customer",
            "customer_phone": item.bill.customer_phone if item.bill else "N/A",
            "payment_method": item.bill.payment_method if item.bill else "Cash",
            "discount": item.bill.discount if item.bill else 0.0,
            "tax": item.bill.tax if item.bill else 0.0,
            "bill_number": item.bill.bill_number if item.bill else f"BILL-2026-{item.bill_id}"
        })
    return result