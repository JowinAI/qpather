from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new organization subscription
@router.post("/organization-subscriptions/", response_model=schemas.OrganizationSubscription)
def create_organization_subscription(subscription: schemas.OrganizationSubscriptionCreate, db: Session = Depends(get_db)):
    db_subscription = db.query(models.OrganizationSubscription).filter(
        models.OrganizationSubscription.OrganizationId == subscription.OrganizationId,
        models.OrganizationSubscription.SubscriptionPlanId == subscription.SubscriptionPlanId
    ).first()
    
    if db_subscription:
        raise HTTPException(status_code=400, detail="Subscription for this organization already exists")
    
    new_subscription = models.OrganizationSubscription(
        OrganizationId=subscription.OrganizationId,
        SubscriptionPlanId=subscription.SubscriptionPlanId,
        StartDate=subscription.StartDate,
        EndDate=subscription.EndDate,
        IsActive=subscription.IsActive,
        CreatedBy=subscription.CreatedBy
    )
    
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

# Get organization subscription by OrganizationId and SubscriptionPlanId
@router.get("/organization-subscriptions/{organization_id}/{subscription_plan_id}", response_model=schemas.OrganizationSubscription)
def get_organization_subscription(organization_id: int, subscription_plan_id: int, db: Session = Depends(get_db)):
    subscription = db.query(models.OrganizationSubscription).filter(
        models.OrganizationSubscription.OrganizationId == organization_id,
        models.OrganizationSubscription.SubscriptionPlanId == subscription_plan_id
    ).first()
    
    if subscription is None:
        raise HTTPException(status_code=404, detail="Organization subscription not found")
    return subscription

# Get all organization subscriptions
@router.get("/organization-subscriptions/", response_model=List[schemas.OrganizationSubscription])
def get_organization_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscriptions = db.query(models.OrganizationSubscription).order_by(models.OrganizationSubscription.SubscriptionPlanId).offset(skip).limit(limit).all()
    return subscriptions

# Update organization subscription
@router.put("/organization-subscriptions/{organization_id}/{subscription_plan_id}", response_model=schemas.OrganizationSubscription)
def update_organization_subscription(organization_id: int, subscription_plan_id: int, subscription: schemas.OrganizationSubscription, db: Session = Depends(get_db)):
    db_subscription = db.query(models.OrganizationSubscription).filter(
        models.OrganizationSubscription.OrganizationId == organization_id,
        models.OrganizationSubscription.SubscriptionPlanId == subscription_plan_id
    ).first()
    
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Organization subscription not found")
    
    db_subscription.StartDate = subscription.StartDate
    db_subscription.EndDate = subscription.EndDate
    db_subscription.IsActive = subscription.IsActive
    db_subscription.UpdatedBy = subscription.UpdatedBy
    
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

# Delete organization subscription
@router.delete("/organization-subscriptions/{organization_id}/{subscription_plan_id}", response_model=schemas.OrganizationSubscription)
def delete_organization_subscription(organization_id: int, subscription_plan_id: int, db: Session = Depends(get_db)):
    db_subscription = db.query(models.OrganizationSubscription).filter(
        models.OrganizationSubscription.OrganizationId == organization_id,
        models.OrganizationSubscription.SubscriptionPlanId == subscription_plan_id
    ).first()
    
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Organization subscription not found")
    
    db.delete(db_subscription)
    db.commit()
    return db_subscription
