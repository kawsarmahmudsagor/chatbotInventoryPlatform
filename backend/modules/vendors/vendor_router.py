from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from backend.db.database import get_db
from chatbot.chatbotInventoryPlatform.backend.modules.vendors.vendor_schema import VendorCreate, VendorRead, VendorUpdate
from chatbot.chatbotInventoryPlatform.backend.modules.vendors import operations as vendor_ops
from chatbot.chatbotInventoryPlatform.backend.modules.vendors.vendor_model import Vendor
from backend.core import auth_vendor

router = APIRouter(prefix="/vendors", tags=["Vendors"])

# --- Create Vendor (Public) ---
@router.post("/create", response_model=VendorRead)
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    new_vendor = vendor_ops.create_vendor(db, vendor)
    if not new_vendor:
        raise HTTPException(status_code=400, detail="Email already registered")
    return new_vendor

# --- List Vendors ---
@router.get("/all-vendors", response_model=List[VendorRead])
def list_vendors(db: Session = Depends(get_db)):
    return vendor_ops.list_vendors(db)

# --- Get Vendor by ID ---
@router.get("/{vendor_id}", response_model=VendorRead)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = vendor_ops.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

# --- Update Vendor (Authenticated) ---
@router.put("/update/{vendor_id}", response_model=VendorRead)
def update_vendor(
    vendor_id: int,
    vendor_data: VendorUpdate,
    db: Session = Depends(get_db),
    current_vendor: Vendor = Depends(auth_vendor.get_current_vendor)
):
    updated_vendor = vendor_ops.update_vendor(db, vendor_id, vendor_data)
    if not updated_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return updated_vendor

# --- Delete Vendor (Authen
