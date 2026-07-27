from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import bill_crud
from schemas import BillCreate, BillUpdate, BillItemCreate
from utils.auth import get_current_user
import models

router = APIRouter(prefix="/bills", tags=["Billing"])


@router.post("/", response_model=dict)
def create_bill(
    bill_data: BillCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new draft bill"""
    # ← FIXED: Pass user_id
    result = bill_crud.create_bill(db, bill_data, current_user.id)
    
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create bill")
    
    return {
        "id": result.id,
        "bill_number": result.bill_number,
        "customer_name": result.customer_name,
        "customer_phone": result.customer_phone,
        "customer_email": result.customer_email,
        "status": result.status,
        "subtotal": result.subtotal,
        "discount": result.discount,
        "tax": result.tax,
        "grand_total": result.grand_total,
        "created_date": result.created_date
    }


def format_bill_dict(bill: Bill) -> dict:
    return {
        "id": bill.id,
        "bill_number": bill.bill_number,
        "customer_name": bill.customer_name,
        "customer_phone": bill.customer_phone,
        "customer_email": bill.customer_email,
        "status": bill.status,
        "subtotal": bill.subtotal,
        "discount": bill.discount,
        "tax": bill.tax,
        "grand_total": bill.grand_total,
        "payment_method": bill.payment_method,
        "payment_status": bill.payment_status,
        "created_date": bill.created_date,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "sku": item.sku,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            }
            for item in (bill.items or [])
        ]
    }


@router.get("/{bill_id}", response_model=dict)
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific bill with items"""
    bill = bill_crud.get_bill(db, bill_id, current_user.id)
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    return format_bill_dict(bill)


@router.get("/", response_model=list[dict])
def get_all_bills(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all bills for the logged-in user"""
    bills = bill_crud.get_all_bills(db, current_user.id)
    
    result = []
    for bill in bills:
        result.append({
            "id": bill.id,
            "bill_number": bill.bill_number,
            "customer_name": bill.customer_name,
            "customer_phone": bill.customer_phone,
            "status": bill.status,
            "payment_status": bill.payment_status,
            "subtotal": bill.subtotal,
            "discount": bill.discount,
            "tax": bill.tax,
            "grand_total": bill.grand_total,
            "payment_method": bill.payment_method,
            "created_date": bill.created_date,
            "items_count": len(bill.items)
        })
    
    return result


@router.post("/{bill_id}/items", response_model=dict)
def add_item_to_bill(
    bill_id: int,
    item_data: BillItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add an item to a bill and return updated bill"""
    result = bill_crud.add_item_to_bill(db, bill_id, item_data, current_user.id)
    
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    
    updated_bill = bill_crud.get_bill(db, bill_id, current_user.id)
    return format_bill_dict(updated_bill)


@router.delete("/{bill_id}/items/{item_id}", response_model=dict)
def remove_item_from_bill(
    bill_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove an item from a bill and return updated bill"""
    result = bill_crud.remove_item_from_bill(db, bill_id, item_id, current_user.id)
    
    if isinstance(result, str) and result != "item_removed":
        raise HTTPException(status_code=400, detail=result)
    
    updated_bill = bill_crud.get_bill(db, bill_id, current_user.id)
    return format_bill_dict(updated_bill)


@router.put("/{bill_id}", response_model=dict)
def update_bill(
    bill_id: int,
    bill_update: BillUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update bill details (customer info, discount, tax, payment method)"""
    # ← FIXED: Pass user_id
    result = bill_crud.update_bill_details(db, bill_id, bill_update, current_user.id)
    
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    
    return {
        "id": result.id,
        "bill_number": result.bill_number,
        "customer_name": result.customer_name,
        "discount": result.discount,
        "tax": result.tax,
        "grand_total": result.grand_total,
        "payment_method": result.payment_method
    }


@router.post("/{bill_id}/finalize", response_model=dict)
def finalize_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Finalize a bill and create sales"""
    # ← FIXED: Pass user_id
    result = bill_crud.finalize_bill(db, bill_id, current_user.id)
    
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    
    return result


@router.delete("/{bill_id}", response_model=dict)
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a bill"""
    # ← FIXED: Pass user_id
    result = bill_crud.delete_bill(db, bill_id, current_user.id)
    
    if result != "success":
        raise HTTPException(status_code=400, detail=result)
    
    return {"message": "Bill deleted successfully"}


@router.get("/status/{status_filter}", response_model=list[dict])
def get_bills_by_status(
    status_filter: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get bills filtered by status (draft/finalized)"""
    if status_filter not in ["draft", "finalized"]:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    
    bills = bill_crud.get_bills_by_status(db, current_user.id, status_filter)
    
    result = []
    for bill in bills:
        result.append({
            "id": bill.id,
            "bill_number": bill.bill_number,
            "customer_name": bill.customer_name,
            "status": bill.status,
            "grand_total": bill.grand_total,
            "created_date": bill.created_date
        })
    
    return result
