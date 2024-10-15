from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new organization setting
@router.post("/organization-settings/", response_model=schemas.OrganizationSettings)
def create_organization_settings(organization_settings: schemas.OrganizationSettingsCreate, db: Session = Depends(get_db)):
    db_organization_settings = db.query(models.OrganizationSettings).filter(
        models.OrganizationSettings.OrganizationId == organization_settings.OrganizationId
    ).first()
    if db_organization_settings:
        raise HTTPException(status_code=400, detail="Organization settings already exist for this organization")
    
    new_organization_settings = models.OrganizationSettings(
        OrganizationId=organization_settings.OrganizationId,
        BusinessSector=organization_settings.BusinessSector,
        CompanySize=organization_settings.CompanySize,
        TeamStructure=organization_settings.TeamStructure,
        GeographicFocus=organization_settings.GeographicFocus,
        HistoricalData=organization_settings.HistoricalData,
        CreatedBy=organization_settings.CreatedBy
    )
    db.add(new_organization_settings)
    db.commit()
    db.refresh(new_organization_settings)
    return new_organization_settings

# Get organization settings by OrganizationId
@router.get("/organization-settings/{organization_id}", response_model=schemas.OrganizationSettings)
def get_organization_settings(organization_id: int, db: Session = Depends(get_db)):
    organization_settings = db.query(models.OrganizationSettings).filter(
        models.OrganizationSettings.OrganizationId == organization_id
    ).first()
    if organization_settings is None:
        raise HTTPException(status_code=404, detail="Organization settings not found")
    return organization_settings

# Get all organization settings
@router.get("/organization-settings/", response_model=List[schemas.OrganizationSettings])
def get_organization_settings_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    organization_settings = db.query(models.OrganizationSettings).order_by(models.OrganizationSettings.OrganizationId).offset(skip).limit(limit).all()
    return organization_settings

# Update organization settings by OrganizationId
@router.put("/organization-settings/{organization_id}", response_model=schemas.OrganizationSettings)
def update_organization_settings(organization_id: int, organization_settings: schemas.OrganizationSettingsUpdate, db: Session = Depends(get_db)):
    db_organization_settings = db.query(models.OrganizationSettings).filter(
        models.OrganizationSettings.OrganizationId == organization_id
    ).first()
    if db_organization_settings is None:
        raise HTTPException(status_code=404, detail="Organization settings not found")
    
    db_organization_settings.BusinessSector = organization_settings.BusinessSector
    db_organization_settings.CompanySize = organization_settings.CompanySize
    db_organization_settings.TeamStructure = organization_settings.TeamStructure
    db_organization_settings.GeographicFocus = organization_settings.GeographicFocus
    db_organization_settings.HistoricalData = organization_settings.HistoricalData
    db_organization_settings.UpdatedBy = organization_settings.UpdatedBy
    db.commit()
    db.refresh(db_organization_settings)
    return db_organization_settings

# Delete organization settings by OrganizationId
@router.delete("/organization-settings/{organization_id}", response_model=schemas.OrganizationSettings)
def delete_organization_settings(organization_id: int, db: Session = Depends(get_db)):
    db_organization_settings = db.query(models.OrganizationSettings).filter(
        models.OrganizationSettings.OrganizationId == organization_id
    ).first()
    if db_organization_settings is None:
        raise HTTPException(status_code=404, detail="Organization settings not found")
    
    db.delete(db_organization_settings)
    db.commit()
    return db_organization_settings
