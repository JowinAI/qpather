from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new user
@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.Email == user.Email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(
        OrganizationId=user.OrganizationId,
        DepartmentId=user.DepartmentId,
        FirstName=user.FirstName,
        LastName=user.LastName,
        Email=user.Email,
        Role=user.Role,
        CreatedBy=user.CreatedBy
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Get user by ID
@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.Id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Get all users
@router.get("/users/", response_model=list[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# Update user by ID
@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.Id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.OrganizationId = user.OrganizationId
    db_user.DepartmentId = user.DepartmentId
    db_user.FirstName = user.FirstName
    db_user.LastName = user.LastName
    db_user.Email = user.Email
    db_user.Role = user.Role
    db_user.UpdatedBy = user.UpdatedBy
    db.commit()
    db.refresh(db_user)
    return db_user

# Delete user by ID
@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.Id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return db_user
