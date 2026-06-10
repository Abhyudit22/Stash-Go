from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import return_crud
from schemas import ReturnCreate, ReturnResponse
from utils.auth import get_current_user  # ← Add this import

router = APIRouter(prefix="/returns", tags=["Returns"])


@router.post("/create", response_model=ReturnResponse)
def create_return(
    return_data: ReturnCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ← Add this
):
    result = return_crud.create_return(db, return_data)
    
    if result == "sale_not_found":
        raise HTTPException(status_code=404, detail="Sale not found")
    
    if result == "product_mismatch":
        raise HTTPException(status_code=400, detail="Product does not match the original sale")
    
    if result == "quantity_exceeds_sale":
        raise HTTPException(status_code=400, detail="Cannot return more than originally purchased")
    
    result.product_id = result.product.id
    
    return result


@router.get("/all_returns", response_model=list[ReturnResponse])
def get_all_returns(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ← Add this
):
    returns = return_crud.get_all_returns(db)
    
    for return_item in returns:
        return_item.product_id = return_item.product.id
    return returns


@router.get("/{return_id}", response_model=ReturnResponse)
def get_return_by_id(
    return_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ← Add this
):
    return_item = return_crud.get_return_by_id(db, return_id)
    
    if return_item is None:
        raise HTTPException(status_code=404, detail="Return not found")
    
    return_item.product_id = return_item.product.id
    
    return return_item


@router.get("/sale/{sale_id}", response_model=list[ReturnResponse])
def get_returns_by_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ← Add this
):
    returns = return_crud.get_returns_by_sale(db, sale_id)
    
    for return_item in returns:
        return_item.product_id = return_item.product.id
    
    return returns