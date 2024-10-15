from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new subscription plan
@router.post("/subscription-plans/", response_model=schemas.SubscriptionPlan)
def create_subscription_plan(subscription_plan: schemas.SubscriptionPlanCreate, db: Session = Depends(get_db)):
    new_subscription_plan = models.SubscriptionPlan(
        PlanName=subscription_plan.PlanName,
        Price=subscription_plan.Price,
        Features=subscription_plan.Features,
        CreatedBy=subscription_plan.CreatedBy
    )
    db.add(new_subscription_plan)
    db.commit()
    db.refresh(new_subscription_plan)
    return new_subscription_plan

# Get subscription plan by ID
@router.get("/subscription-plans/{subscription_plan_id}", response_model=schemas.SubscriptionPlan)
def get_subscription_plan(subscription_plan_id: int, db: Session = Depends(get_db)):
    subscription_plan = db.query(models.SubscriptionPlan).filter(models.SubscriptionPlan.Id == subscription_plan_id).first()
    if subscription_plan is None:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    return subscription_plan

# Get all subscription plans
@router.get("/subscription-plans/", response_model=List[schemas.SubscriptionPlan])
def get_subscription_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscription_plans = db.query(models.SubscriptionPlan).order_by(models.SubscriptionPlan.Id).offset(skip).limit(limit).all()
    return subscription_plans

# Update subscription plan by ID
@router.put("/subscription-plans/{subscription_plan_id}", response_model=schemas.SubscriptionPlan)
def update_subscription_plan(subscription_plan_id: int, subscription_plan: schemas.SubscriptionPlanUpdate, db: Session = Depends(get_db)):
    db_subscription_plan = db.query(models.SubscriptionPlan).filter(models.SubscriptionPlan.Id == subscription_plan_id).first()
    if db_subscription_plan is None:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    db_subscription_plan.PlanName = subscription_plan.PlanName
    db_subscription_plan.Price = subscription_plan.Price
    db_subscription_plan.Features = subscription_plan.Features
    db_subscription_plan.UpdatedBy = subscription_plan.UpdatedBy
    db.commit()
    db.refresh(db_subscription_plan)
    return db_subscription_plan

# Delete subscription plan by ID
@router.delete("/subscription-plans/{subscription_plan_id}", response_model=schemas.SubscriptionPlan)
def delete_subscription_plan(subscription_plan_id: int, db: Session = Depends(get_db)):
    db_subscription_plan = db.query(models.SubscriptionPlan).filter(models.SubscriptionPlan.Id == subscription_plan_id).first()
    if db_subscription_plan is None:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    db.delete(db_subscription_plan)
    db.commit()
    return db_subscription_plan
