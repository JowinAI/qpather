from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new feature
@router.post("/features/", response_model=schemas.Feature)
def create_feature(feature: schemas.FeatureCreate, db: Session = Depends(get_db)):
    new_feature = models.Feature(
        FeatureName=feature.FeatureName,
        Description=feature.Description,
    )
    db.add(new_feature)
    db.commit()
    db.refresh(new_feature)
    return new_feature

# Get feature by ID
@router.get("/features/{feature_id}", response_model=schemas.Feature)
def get_feature(feature_id: int, db: Session = Depends(get_db)):
    feature = db.query(models.Feature).filter(models.Feature.Id == feature_id).first()
    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature

# Get all features
@router.get("/features/", response_model=List[schemas.Feature])
def get_features(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    features = db.query(models.Feature).order_by(models.Feature.Id).offset(skip).limit(limit).all()
    return features

# Update feature by ID
@router.put("/features/{feature_id}", response_model=schemas.Feature)
def update_feature(feature_id: int, feature: schemas.FeatureUpdate, db: Session = Depends(get_db)):
    db_feature = db.query(models.Feature).filter(models.Feature.Id == feature_id).first()
    if db_feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    db_feature.FeatureName = feature.FeatureName
    db_feature.Description = feature.Description
    db.commit()
    db.refresh(db_feature)
    return db_feature

# Delete feature by ID
@router.delete("/features/{feature_id}", response_model=schemas.Feature)
def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    db_feature = db.query(models.Feature).filter(models.Feature.Id == feature_id).first()
    if db_feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    db.delete(db_feature)
    db.commit()
    return db_feature
