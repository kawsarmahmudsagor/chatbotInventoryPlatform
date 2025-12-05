from sqlalchemy.orm import Session
from typing import List
from chatbot.chatbotInventoryPlatform.backend.modules.vendors.vendor_model import Vendor
from chatbot.chatbotInventoryPlatform.backend.modules.vendors.vendor_schema import VendorCreate, VendorUpdate
from backend.core import auth_vendor

# -------------------------
# Vendors CRUD Operations
# -------------------------

def create_vendor(db: Session, vendor_data: VendorCreate) -> Vendor:
    db_vendor = db.query(Vendor).filter(Vendor.email == vendor_data.email).first()
    if db_vendor:
        return None

    hashed_password = auth_vendor.get_password_hash(vendor_data.password)

    new_vendor = Vendor(
        **vendor_data.dict(exclude={"password"}),
        hashed_password=hashed_password
    )

    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor

def list_vendors(db: Session) -> List[Vendor]:
    return db.query(Vendor).all()

def get_vendor(db: Session, vendor_id: int) -> Vendor:
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()

def update_vendor(db: Session, vendor_id: int, vendor_data: VendorUpdate) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return None
    for key, value in vendor_data.dict().items():
        setattr(vendor, key, value)
    db.commit()
    db.refresh(vendor)
    return vendor

def delete_vendor(db: Session, vendor_id: int) -> bool:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return False
    db.delete(vendor)
    db.commit()
    return True
