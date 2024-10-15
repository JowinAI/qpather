from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new assignment user
@router.post("/assignment-users/", response_model=schemas.AssignmentUser)
def create_assignment_user(assignment_user: schemas.AssignmentUserCreate, db: Session = Depends(get_db)):
    db_assignment_user = db.query(models.AssignmentUser).filter(
        models.AssignmentUser.AssignmentId == assignment_user.AssignmentId,
        models.AssignmentUser.AssignedTo == assignment_user.AssignedTo
    ).first()
    if db_assignment_user:
        raise HTTPException(status_code=400, detail="Assignment user already exists")
    
    new_assignment_user = models.AssignmentUser(
        AssignmentId=assignment_user.AssignmentId,
        AssignedTo=assignment_user.AssignedTo,
        CreatedBy=assignment_user.CreatedBy
    )
    db.add(new_assignment_user)
    db.commit()
    db.refresh(new_assignment_user)
    return new_assignment_user

# Get assignment user by AssignmentId and AssignedTo
@router.get("/assignment-users/{assignment_id}/{assigned_to}", response_model=schemas.AssignmentUser)
def get_assignment_user(assignment_id: int, assigned_to: str, db: Session = Depends(get_db)):
    assignment_user = db.query(models.AssignmentUser).filter(
        models.AssignmentUser.AssignmentId == assignment_id,
        models.AssignmentUser.AssignedTo == assigned_to
    ).first()
    if assignment_user is None:
        raise HTTPException(status_code=404, detail="Assignment user not found")
    return assignment_user

# Get all assignment users
@router.get("/assignment-users/", response_model=List[schemas.AssignmentUser])
def get_assignment_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assignment_users = db.query(models.AssignmentUser).order_by(models.AssignmentUser.AssignmentId).offset(skip).limit(limit).all()
    return assignment_users

# Update assignment user
@router.put("/assignment-users/{assignment_id}/{assigned_to}", response_model=schemas.AssignmentUser)
def update_assignment_user(assignment_id: int, assigned_to: str, assignment_user: schemas.AssignmentUser, db: Session = Depends(get_db)):
    db_assignment_user = db.query(models.AssignmentUser).filter(
        models.AssignmentUser.AssignmentId == assignment_id,
        models.AssignmentUser.AssignedTo == assigned_to
    ).first()
    if db_assignment_user is None:
        raise HTTPException(status_code=404, detail="Assignment user not found")
    
    db_assignment_user.UpdatedBy = assignment_user.UpdatedBy
    db.commit()
    db.refresh(db_assignment_user)
    return db_assignment_user

# Delete assignment user
@router.delete("/assignment-users/{assignment_id}/{assigned_to}", response_model=schemas.AssignmentUser)
def delete_assignment_user(assignment_id: int, assigned_to: str, db: Session = Depends(get_db)):
    db_assignment_user = db.query(models.AssignmentUser).filter(
        models.AssignmentUser.AssignmentId == assignment_id,
        models.AssignmentUser.AssignedTo == assigned_to
    ).first()
    if db_assignment_user is None:
        raise HTTPException(status_code=404, detail="Assignment user not found")
    
    db.delete(db_assignment_user)
    db.commit()
    return db_assignment_user
