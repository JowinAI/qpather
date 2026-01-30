from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from db import models, schemas
from api.dependencies.model_utils import get_db
import jwt
from jwt import PyJWTError 
import json
import os
from typing import Optional

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-tokens-change-this-in-prod")
ALGORITHM = "HS256"

# Helper to get user from token
async def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Token")
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
             raise HTTPException(status_code=401, detail="Invalid Token")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    user = db.query(models.User).filter(models.User.Email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# GET User Defaults
@router.get("/users/me/dashboard-settings", response_model=Optional[schemas.DashboardSettingsPayload])
def get_user_dashboard_settings(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    settings_obj = db.query(models.DashboardSettings).filter(
        models.DashboardSettings.UserId == current_user.Id,
        models.DashboardSettings.GoalId == None
    ).first()
    
    if not settings_obj:
        return None
        
    return json.loads(settings_obj.Settings)

# PUT User Defaults
@router.put("/users/me/dashboard-settings", response_model=schemas.DashboardSettingsPayload)
def update_user_dashboard_settings(payload: schemas.DashboardSettingsPayload, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    settings_obj = db.query(models.DashboardSettings).filter(
        models.DashboardSettings.UserId == current_user.Id,
        models.DashboardSettings.GoalId == None
    ).first()
    
    # Pydantic v2 use model_dump_json()
    settings_json = payload.model_dump_json()
    
    if settings_obj:
        settings_obj.Settings = settings_json
    else:
        settings_obj = models.DashboardSettings(
            UserId=current_user.Id,
            GoalId=None,
            Settings=settings_json
        )
        db.add(settings_obj)
    
    db.commit()
    db.refresh(settings_obj)
    return payload

# GET Goal Settings
@router.get("/goals/{goal_id}/dashboard-settings", response_model=Optional[schemas.DashboardSettingsPayload])
def get_goal_dashboard_settings(goal_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    settings_obj = db.query(models.DashboardSettings).filter(
        models.DashboardSettings.UserId == current_user.Id,
        models.DashboardSettings.GoalId == goal_id
    ).first()
    
    if not settings_obj:
        return None
    
    return json.loads(settings_obj.Settings)

# PUT Goal Settings (Save for this Goal)
@router.put("/goals/{goal_id}/dashboard-settings", response_model=schemas.DashboardSettingsPayload)
def update_goal_dashboard_settings(goal_id: int, payload: schemas.DashboardSettingsPayload, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    settings_obj = db.query(models.DashboardSettings).filter(
        models.DashboardSettings.UserId == current_user.Id,
        models.DashboardSettings.GoalId == goal_id
    ).first()
    
    settings_json = payload.model_dump_json()
    
    if settings_obj:
        settings_obj.Settings = settings_json
    else:
        settings_obj = models.DashboardSettings(
            UserId=current_user.Id,
            GoalId=goal_id,
            Settings=settings_json
        )
        db.add(settings_obj)
        
    db.commit()
    return payload

# DELETE Goal Settings (Reset)
@router.delete("/goals/{goal_id}/dashboard-settings")
def reset_goal_dashboard_settings(goal_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    settings_obj = db.query(models.DashboardSettings).filter(
        models.DashboardSettings.UserId == current_user.Id,
        models.DashboardSettings.GoalId == goal_id
    ).first()
    
    if settings_obj:
        db.delete(settings_obj)
        db.commit()
    
    return {"message": "Goal settings reset"}
