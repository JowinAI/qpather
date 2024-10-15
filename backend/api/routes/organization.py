from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

@router.post("/organizations/", response_model=schemas.Organization)
def create_organization(organization: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    db_org = models.Organization(
        ClientId=organization.ClientId,
        Name=organization.Name,
        ContactEmail=organization.ContactEmail,
        ContactPhone=organization.ContactPhone,
        Address=organization.Address,
        CreatedBy="system_user"
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

@router.get("/organizations/{organization_id}", response_model=schemas.Organization)
def read_organization(organization_id: int, db: Session = Depends(get_db)):
    db_org = db.query(models.Organization).filter(models.Organization.Id == organization_id).first()
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_org

@router.get("/organizations/", response_model=list[schemas.Organization])
def read_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Organization).order_by(models.Organization.Id).offset(skip).limit(limit).all()


@router.put("/organizations/{organization_id}", response_model=schemas.Organization)
def update_organization(organization_id: int, organization: schemas.OrganizationUpdate, db: Session = Depends(get_db)):
    db_org = db.query(models.Organization).filter(models.Organization.Id == organization_id).first()
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db_org.Name = organization.Name
    db_org.ContactEmail = organization.ContactEmail
    db_org.ContactPhone = organization.ContactPhone
    db_org.Address = organization.Address
    db_org.UpdatedBy = "system_user"
    db.commit()
    db.refresh(db_org)
    return db_org

@router.delete("/organizations/{organization_id}", response_model=schemas.Organization)
def delete_organization(organization_id: int, db: Session = Depends(get_db)):
    db_org = db.query(models.Organization).filter(models.Organization.Id == organization_id).first()
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    db.delete(db_org)
    db.commit()
    return db_org
