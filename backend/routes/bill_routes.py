from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import bill_crud
from pydantic import BaseModel
from typing import List, Optional
from utils.auth import get_current_active_user  # ← Add this import

router = APIRouter(prefix="/bills", tags=["Bills"])


class BillItemRequest(BaseModel):
    product_id: int
    quantity: int


class BillRequest(BaseModel):
    items: List[BillItemRequest]
    customer_name: Optional[str] = None
    payment_method: str = "cash"


@router.post("/create")
def create_bill_and_sale(
    bill_request: BillRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Add this
):
    """
    One function: Creates bill AND sale together
    """
    items_list = [{"product_id": item.product_id, "quantity": item.quantity} for item in bill_request.items]
    
    result = bill_crud.create_bill_and_sale(
        db,
        items_list,
        bill_request.customer_name,
        bill_request.payment_method
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result