from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create new user settings
@router.post("/user-settings/", response_model=schemas.UserSettings)
def create_user_settings(user_settings: schemas.UserSettingsCreate, db: Session = Depends(get_db)):
    db_user_settings = db.query(models.UserSettings).filter(
        models.UserSettings.UserId == user_settings.UserId
    ).first()
    if db_user_settings:
        raise HTTPException(status_code=400, detail="User settings already exist for this user")
    
    new_user_settings = models.UserSettings(
        UserId=user_settings.UserId,
        Role=user_settings.Role,
        BusinessObjective=user_settings.BusinessObjective,
        CurrentChallenges=user_settings.CurrentChallenges,
        KPIs=user_settings.KPIs,
        TeamMemberRoles=user_settings.TeamMemberRoles,
        PriorityLevel=user_settings.PriorityLevel,
        LevelOfComplexity=user_settings.LevelOfComplexity,
        TargetOutcome=user_settings.TargetOutcome,
        CommunicationStyle=user_settings.CommunicationStyle,
        GoalTimeframe=user_settings.GoalTimeframe,
        CreatedBy=user_settings.CreatedBy
    )
    db.add(new_user_settings)
    db.commit()
    db.refresh(new_user_settings)
    return new_user_settings

# Get user settings by UserId
@router.get("/user-settings/{user_id}", response_model=schemas.UserSettings)
def get_user_settings(user_id: int, db: Session = Depends(get_db)):
    user_settings = db.query(models.UserSettings).filter(models.UserSettings.UserId == user_id).first()
    if user_settings is None:
        raise HTTPException(status_code=404, detail="User settings not found")
    return user_settings

# Get all user settings
@router.get("/user-settings/", response_model=List[schemas.UserSettings])
def get_user_settings_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user_settings = db.query(models.UserSettings).order_by(models.UserSettings.UserId).offset(skip).limit(limit).all()
    return user_settings

# Update user settings by UserId
@router.put("/user-settings/{user_id}", response_model=schemas.UserSettings)
def update_user_settings(user_id: int, user_settings: schemas.UserSettingsUpdate, db: Session = Depends(get_db)):
    db_user_settings = db.query(models.UserSettings).filter(models.UserSettings.UserId == user_id).first()
    if db_user_settings is None:
        raise HTTPException(status_code=404, detail="User settings not found")
    
    db_user_settings.Role = user_settings.Role
    db_user_settings.BusinessObjective = user_settings.BusinessObjective
    db_user_settings.CurrentChallenges = user_settings.CurrentChallenges
    db_user_settings.KPIs = user_settings.KPIs
    db_user_settings.TeamMemberRoles = user_settings.TeamMemberRoles
    db_user_settings.PriorityLevel = user_settings.PriorityLevel
    db_user_settings.LevelOfComplexity = user_settings.LevelOfComplexity
    db_user_settings.TargetOutcome = user_settings.TargetOutcome
    db_user_settings.CommunicationStyle = user_settings.CommunicationStyle
    db_user_settings.GoalTimeframe = user_settings.GoalTimeframe
    db_user_settings.UpdatedBy = user_settings.UpdatedBy
    db.commit()
    db.refresh(db_user_settings)
    return db_user_settings

# Delete user settings by UserId
@router.delete("/user-settings/{user_id}", response_model=schemas.UserSettings)
def delete_user_settings(user_id: int, db: Session = Depends(get_db)):
    db_user_settings = db.query(models.UserSettings).filter(models.UserSettings.UserId == user_id).first()
    if db_user_settings is None:
        raise HTTPException(status_code=404, detail="User settings not found")
    
    db.delete(db_user_settings)
    db.commit()
    return db_user_settings
