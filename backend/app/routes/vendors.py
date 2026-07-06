from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Vendor
from app.schemas import VendorCreate, VendorResponse


router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("", response_model=VendorResponse)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    existing = db.query(Vendor).filter(Vendor.name == payload.name).first()

    if existing:
        raise HTTPException(status_code=409, detail="Vendor already exists")

    vendor = Vendor(
        vendor_id=f"VEN-{uuid4().hex[:8].upper()}",
        name=payload.name,
        industry=payload.industry,
        country=payload.country,
        risk_rating=payload.risk_rating,
        status=payload.status,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return vendor


@router.get("", response_model=list[VendorResponse])
def list_vendors(
    risk_rating: str | None = None,
    country: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Vendor)

    if risk_rating:
        query = query.filter(Vendor.risk_rating == risk_rating)

    if country:
        query = query.filter(Vendor.country == country)

    return query.order_by(Vendor.created_at.desc()).limit(limit).all()


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: str, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return vendor
