from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import ProductCreate, ProductUpdate, ProductResponse, StockUpdate
from crud import product_crud
from utils.auth import get_current_user

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post("/create", response_model=ProductResponse)
def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # FIXED: Pass current_user.id to check if THIS user already has this SKU
    existing_product = product_crud.get_product_by_sku(db, product.sku, current_user.id)

    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="Product with this SKU already exists in your inventory"
        )

    # FIXED: Pass current_user.id to create the product under their account
    return product_crud.create_product(db, product, current_user.id)


@router.get("/getall", response_model=List[ProductResponse])
def get_all_products(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # FIXED: Uncommented this!
):
    # FIXED: Pass current_user.id so they only see their own products
    return product_crud.get_all_products(db, current_user.id)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # FIXED: Pass current_user.id
    product = product_crud.get_product_by_id(db, product_id, current_user.id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # FIXED: Pass current_user.id
    updated_product = product_crud.update_product(db, product_id, product_data, current_user.id)

    if updated_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return updated_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # FIXED: Pass current_user.id
    deleted_product = product_crud.delete_product(db, product_id, current_user.id)

    if deleted_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return {
        "message": "Product deleted successfully"
    }


@router.patch("/{product_id}/increase-stock", response_model=ProductResponse)
def increase_product_stock(
    product_id: int,
    stock_data: StockUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # FIXED: Pass current_user.id
    updated_product = product_crud.increase_stock(
        db,
        product_id,
        stock_data.quantity,
        current_user.id
    )

    if updated_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return updated_product


@router.patch("/{product_id}/decrease-stock", response_model=ProductResponse)
def decrease_product_stock(
    product_id: int,
    stock_data: StockUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # FIXED: Pass current_user.id
    updated_product = product_crud.decrease_stock(
        db,
        product_id,
        stock_data.quantity,
        current_user.id
    )

    if updated_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if updated_product == "not_enough_stock":
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available"
        )

    return updated_product