from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new response
@router.post("/responses/", response_model=schemas.Response)
def create_response(response: schemas.ResponseCreate, db: Session = Depends(get_db)):
    new_response = models.Response(
        AssignmentId=response.AssignmentId,
        Answer=response.Answer,
        CreatedBy=response.CreatedBy
    )
    db.add(new_response)
    db.commit()
    db.refresh(new_response)
    return new_response

# Get response by ID
@router.get("/responses/{response_id}", response_model=schemas.Response)
def get_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(models.Response).filter(models.Response.Id == response_id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return response

# Get all responses
@router.get("/responses/", response_model=List[schemas.Response])
def get_responses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    responses = db.query(models.Response).order_by(models.Response.Id).offset(skip).limit(limit).all()
    return responses

# Update response by ID
@router.put("/responses/{response_id}", response_model=schemas.Response)
def update_response(response_id: int, response: schemas.ResponseUpdate, db: Session = Depends(get_db)):
    db_response = db.query(models.Response).filter(models.Response.Id == response_id).first()
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    
    db_response.AssignmentId = response.AssignmentId
    db_response.Answer = response.Answer
    db_response.UpdatedBy = response.UpdatedBy
    db.commit()
    db.refresh(db_response)
    return db_response

# Delete response by ID
@router.delete("/responses/{response_id}", response_model=schemas.Response)
def delete_response(response_id: int, db: Session = Depends(get_db)):
    db_response = db.query(models.Response).filter(models.Response.Id == response_id).first()
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    
    db.delete(db_response)
    db.commit()
    return db_response
