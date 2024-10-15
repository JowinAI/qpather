from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new billing entry
@router.post("/billing/", response_model=schemas.Billing)
def create_billing(billing: schemas.BillingCreate, db: Session = Depends(get_db)):
    new_billing = models.Billing(
        OrganizationId=billing.OrganizationId,
        Amount=billing.Amount,
        BillingPeriodStart=billing.BillingPeriodStart,
        BillingPeriodEnd=billing.BillingPeriodEnd,
        Status=billing.Status,
        PaymentDate=billing.PaymentDate,
        CreatedBy=billing.CreatedBy
    )
    db.add(new_billing)
    db.commit()
    db.refresh(new_billing)
    return new_billing

# Get billing entry by ID
@router.get("/billing/{billing_id}", response_model=schemas.Billing)
def get_billing(billing_id: int, db: Session = Depends(get_db)):
    billing = db.query(models.Billing).filter(models.Billing.Id == billing_id).first()
    if billing is None:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return billing

# Get all billing entries
@router.get("/billing/", response_model=List[schemas.Billing])
def get_billing_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    billing_entries = db.query(models.Billing).order_by(models.Billing.Id).offset(skip).limit(limit).all()
    return billing_entries

# Update billing entry by ID
@router.put("/billing/{billing_id}", response_model=schemas.Billing)
def update_billing(billing_id: int, billing: schemas.BillingUpdate, db: Session = Depends(get_db)):
    db_billing = db.query(models.Billing).filter(models.Billing.Id == billing_id).first()
    if db_billing is None:
        raise HTTPException(status_code=404, detail="Billing record not found")
    
    db_billing.Amount = billing.Amount
    db_billing.BillingPeriodStart = billing.BillingPeriodStart
    db_billing.BillingPeriodEnd = billing.BillingPeriodEnd
    db_billing.Status = billing.Status
    db_billing.PaymentDate = billing.PaymentDate
    db_billing.UpdatedBy = billing.UpdatedBy
    db.commit()
    db.refresh(db_billing)
    return db_billing

# Delete billing entry by ID
@router.delete("/billing/{billing_id}", response_model=schemas.Billing)
def delete_billing(billing_id: int, db: Session = Depends(get_db)):
    db_billing = db.query(models.Billing).filter(models.Billing.Id == billing_id).first()
    if db_billing is None:
        raise HTTPException(status_code=404, detail="Billing record not found")
    
    db.delete(db_billing)
    db.commit()
    return db_billing
