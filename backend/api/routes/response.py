from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new user response (merged structure)
@router.post("/user-responses/", response_model=schemas.UserResponse)
def create_user_response(user_response: schemas.UserResponseCreate, db: Session = Depends(get_db)):
    new_user_response = models.UserResponse(
        AssignmentId=user_response.AssignmentId,
        AssignedTo=user_response.AssignedTo,
        Answer=user_response.Answer,
        Status=user_response.Status,  # 'Assigned', 'Draft', 'Final'
        CreatedBy=user_response.CreatedBy
    )
    db.add(new_user_response)
    db.commit()
    db.refresh(new_user_response)
    return new_user_response

# Get user response by ID
@router.get("/user-responses/{response_id}", response_model=schemas.UserResponse)
def get_user_response(response_id: int, db: Session = Depends(get_db)):
    user_response = db.query(models.UserResponse).filter(models.UserResponse.Id == response_id).first()
    if user_response is None:
        raise HTTPException(status_code=404, detail="User response not found")
    return user_response

# Get all user responses
@router.get("/user-responses/", response_model=List[schemas.UserResponse])
def get_user_responses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user_responses = db.query(models.UserResponse).order_by(models.UserResponse.Id).offset(skip).limit(limit).all()
    return user_responses

# Update user response by ID
@router.put("/user-responses/{response_id}", response_model=schemas.UserResponse)
def update_user_response(response_id: int, user_response: schemas.UserResponseUpdate, db: Session = Depends(get_db)):
    db_user_response = db.query(models.UserResponse).filter(models.UserResponse.Id == response_id).first()
    if db_user_response is None:
        raise HTTPException(status_code=404, detail="User response not found")
    
    db_user_response.AssignmentId = user_response.AssignmentId
    db_user_response.AssignedTo = user_response.AssignedTo
    db_user_response.Answer = user_response.Answer
    db_user_response.Status = user_response.Status
    db_user_response.UpdatedBy = user_response.UpdatedBy
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

# Delete user response by ID
@router.delete("/user-responses/{response_id}", response_model=schemas.UserResponse)
def delete_user_response(response_id: int, db: Session = Depends(get_db)):
    db_user_response = db.query(models.UserResponse).filter(models.UserResponse.Id == response_id).first()
    if db_user_response is None:
        raise HTTPException(status_code=404, detail="User response not found")
    
    db.delete(db_user_response)
    db.commit()
    return db_user_response
