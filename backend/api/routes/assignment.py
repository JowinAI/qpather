from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new assignment
@router.post("/assignments/", response_model=schemas.Assignment)
def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db)):
    new_assignment = models.Assignment(
        GoalId=assignment.GoalId,
        ParentAssignmentId=assignment.ParentAssignmentId,
        QuestionText=assignment.QuestionText,
        Order=assignment.Order,
        CreatedBy=assignment.CreatedBy
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

# Get assignment by ID
@router.get("/assignments/{assignment_id}", response_model=schemas.Assignment)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(models.Assignment).filter(models.Assignment.Id == assignment_id).first()
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

# Get all assignments
@router.get("/assignments/", response_model=List[schemas.Assignment])
def get_assignments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assignments = db.query(models.Assignment).order_by(models.Assignment.Id).offset(skip).limit(limit).all()
    return assignments

# Update assignment by ID
@router.put("/assignments/{assignment_id}", response_model=schemas.Assignment)
def update_assignment(assignment_id: int, assignment: schemas.AssignmentUpdate, db: Session = Depends(get_db)):
    db_assignment = db.query(models.Assignment).filter(models.Assignment.Id == assignment_id).first()
    if db_assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db_assignment.GoalId = assignment.GoalId
    db_assignment.ParentAssignmentId = assignment.ParentAssignmentId
    db_assignment.QuestionText = assignment.QuestionText
    db_assignment.Order = assignment.Order
    db_assignment.UpdatedBy = assignment.UpdatedBy
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

# Delete assignment by ID
@router.delete("/assignments/{assignment_id}", response_model=schemas.Assignment)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_assignment = db.query(models.Assignment).filter(models.Assignment.Id == assignment_id).first()
    if db_assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(db_assignment)
    db.commit()
    return db_assignment
