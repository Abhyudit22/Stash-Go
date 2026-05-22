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
    
    return result


@router.get("/", response_model=list[SaleResponse])
def get_all_sales(db: Session = Depends(get_db)):
    sales = sale_crud.get_all_sales(db)
  
    for sale in sales:
        sale.product_name = sale.product.name
    
    return sales


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale_by_id(sale_id: int, db: Session = Depends(get_db)):
    sale = sale_crud.get_sale_by_id(db, sale_id)
    
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    sale.product_name = sale.product.name
    
    return sale


@router.get("/product/{product_id}", response_model=list[SaleResponse])
def get_sales_by_product(product_id: int, db: Session = Depends(get_db)):
    sales = sale_crud.get_sales_by_product(db, product_id)
    
    for sale in sales:
        sale.product_name = sale.product.name
    
    return sales