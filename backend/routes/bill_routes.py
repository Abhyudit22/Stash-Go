from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import bill_crud
from schemas import BillCreate, BillItemCreate, BillUpdate, BillResponse
from utils.auth import get_current_active_user  # ← Only import this, not admin
from typing import List

router = APIRouter(prefix="/bills", tags=["Bills"])


@router.post("/", response_model=BillResponse)
def create_bill(
    bill_data: BillCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Any logged-in user
):
    """Create a new draft bill (NO sale created, NO stock deducted)"""
    return bill_crud.create_bill(db, bill_data)


@router.post("/{bill_id}/items", response_model=BillResponse)
def add_item_to_bill(
    bill_id: int,
    item_data: BillItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Any logged-in user
):
    """Add item to draft bill"""
    result = bill_crud.add_item_to_bill(db, bill_id, item_data)
    
    if result == "bill_not_found":
        raise HTTPException(status_code=404, detail="Bill not found")
    if result == "bill_not_draft":
        raise HTTPException(status_code=400, detail="Can only add items to draft bills")
    if result == "product_not_found":
        raise HTTPException(status_code=404, detail="Product not found")
    if result == "insufficient_stock":
        raise HTTPException(status_code=400, detail="Insufficient stock available")
    
    return bill_crud.get_bill(db, bill_id)


@router.delete("/{bill_id}/items/{item_id}", response_model=BillResponse)
def remove_item_from_bill(
    bill_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Any logged-in user
):
    """Remove item from draft bill"""
    result = bill_crud.remove_item_from_bill(db, bill_id, item_id)
    
    if result == "bill_not_found":
        raise HTTPException(status_code=404, detail="Bill not found")
    if result == "bill_not_draft":
        raise HTTPException(status_code=400, detail="Can only remove items from draft bills")
    if result == "item_not_found":
        raise HTTPException(status_code=404, detail="Item not found")
    
    return bill_crud.get_bill(db, bill_id)


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill_update: BillUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Any logged-in user
):
    """Update bill details (customer, discount, tax, payment method)"""
    result = bill_crud.update_bill_details(db, bill_id, bill_update)
    
    if result == "bill_not_found":
        raise HTTPException(status_code=404, detail="Bill not found")
    if result == "bill_not_draft":
        raise HTTPException(status_code=400, detail="Can only update draft bills")
    
    return result


@router.post("/{bill_id}/finalize")
def finalize_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Any logged-in user
):
    """Finalize bill - THIS creates sales and deducts stock"""
    result = bill_crud.finalize_bill(db, bill_id, current_user.id)
    
    if result == "bill_not_found":
        raise HTTPException(status_code=404, detail="Bill not found")
    if result == "bill_not_draft":
        raise HTTPException(status_code=400, detail="Bill is already finalized")
    if result == "bill_empty":
        raise HTTPException(status_code=400, detail="Cannot finalize empty bill")
    if result == "payment_method_required":
        raise HTTPException(status_code=400, detail="Payment method required")
    if isinstance(result, str) and result.startswith("insufficient_stock"):
        raise HTTPException(status_code=400, detail="Insufficient stock for one or more items")
    
    return result


@router.get("/", response_model=List[BillResponse])
def get_all_bills(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Any logged-in user
):
    """Get all bills"""
    return bill_crud.get_all_bills(db)


@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  # ← Any logged-in user
):
    """Get bill by ID with all items"""
    bill = bill_crud.get_bill(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.delete("/{bill_id}")
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)  
):
    
    result = bill_crud.delete_bill(db, bill_id)
    
    if result == "bill_not_found":
        raise HTTPException(status_code=404, detail="Bill not found")
    if result == "cannot_delete_finalized":
        raise HTTPException(status_code=400, detail="Cannot delete finalized bill")
    
    return {"message": "Bill deleted successfully"}