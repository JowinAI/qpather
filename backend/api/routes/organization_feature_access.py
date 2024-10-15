from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db
from datetime import datetime


router = APIRouter()

# Create a new organization feature access entry
@router.post("/organization-feature-access/", response_model=schemas.OrganizationFeatureAccess)
def create_organization_feature_access(access: schemas.OrganizationFeatureAccessCreate, db: Session = Depends(get_db)):
    # Check if a record with the same OrganizationId and FeatureId exists
    existing_access = db.query(models.OrganizationFeatureAccess).filter(
        models.OrganizationFeatureAccess.OrganizationId == access.OrganizationId,
        models.OrganizationFeatureAccess.FeatureId == access.FeatureId
    ).first()

    if existing_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feature access already exists for this organization."
        )

    # If it doesn't exist, create a new record
    db_access = models.OrganizationFeatureAccess(
        OrganizationId=access.OrganizationId,
        FeatureId=access.FeatureId,
        AccessGranted=access.AccessGranted,
    )
    db.add(db_access)
    db.commit()
    db.refresh(db_access)

    return db_access
    

# Get an organization feature access entry by OrganizationId and FeatureId
@router.get("/organization-feature-access/{organization_id}/{feature_id}", response_model=schemas.OrganizationFeatureAccess)
def get_organization_feature_access(organization_id: int, feature_id: int, db: Session = Depends(get_db)):
    access = db.query(models.OrganizationFeatureAccess).filter(
        models.OrganizationFeatureAccess.OrganizationId == organization_id,
        models.OrganizationFeatureAccess.FeatureId == feature_id
    ).first()
    
    if access is None:
        raise HTTPException(status_code=404, detail="Organization feature access not found")
    return access

# Get all organization feature access entries
@router.get("/organization-feature-access/", response_model=List[schemas.OrganizationFeatureAccess])
def get_organization_feature_access_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    accesses = db.query(models.OrganizationFeatureAccess).order_by(models.OrganizationFeatureAccess.OrganizationId).offset(skip).limit(limit).all()
    return accesses

# Update organization feature access by OrganizationId and FeatureId
@router.put("/organization-feature-access/{organization_id}/{feature_id}", response_model=schemas.OrganizationFeatureAccess)
def update_organization_feature_access(organization_id: int, feature_id: int, access: schemas.OrganizationFeatureAccess, db: Session = Depends(get_db)):
    db_access = db.query(models.OrganizationFeatureAccess).filter(
        models.OrganizationFeatureAccess.OrganizationId == organization_id,
        models.OrganizationFeatureAccess.FeatureId == feature_id
    ).first()
    
    if db_access is None:
        raise HTTPException(status_code=404, detail="Organization feature access not found")
    
    db_access.AccessGranted = access.AccessGranted
    db.commit()
    db.refresh(db_access)
    return db_access

# Delete an organization feature access entry by OrganizationId and FeatureId
@router.delete("/organization-feature-access/{organization_id}/{feature_id}", response_model=schemas.OrganizationFeatureAccess)
def delete_organization_feature_access(organization_id: int, feature_id: int, db: Session = Depends(get_db)):
    db_access = db.query(models.OrganizationFeatureAccess).filter(
        models.OrganizationFeatureAccess.OrganizationId == organization_id,
        models.OrganizationFeatureAccess.FeatureId == feature_id
    ).first()
    
    if db_access is None:
        raise HTTPException(status_code=404, detail="Organization feature access not found")
    
    db.delete(db_access)
    db.commit()
    return db_access
