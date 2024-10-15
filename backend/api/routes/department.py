from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

@router.post("/departments/", response_model=schemas.Department)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    db_dept = models.Department(
        OrganizationId=department.OrganizationId,
        Name=department.Name,
        ManagerName=department.ManagerName,
        CreatedBy="system_user"
    )
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.get("/departments/{department_id}", response_model=schemas.Department)
def read_department(department_id: int, db: Session = Depends(get_db)):
    db_dept = db.query(models.Department).filter(models.Department.Id == department_id).first()
    if db_dept is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_dept

@router.get("/departments/", response_model=list[schemas.Department])
def read_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Department).order_by(models.Department.Id).offset(skip).limit(limit).all()


@router.put("/departments/{department_id}", response_model=schemas.Department)
def update_department(department_id: int, department: schemas.DepartmentUpdate, db: Session = Depends(get_db)):
    db_dept = db.query(models.Department).filter(models.Department.Id == department_id).first()
    if db_dept is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db_dept.Name = department.Name
    db_dept.ManagerName = department.ManagerName
    db_dept.UpdatedBy = "system_user"
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.delete("/departments/{department_id}", response_model=schemas.Department)
def delete_department(department_id: int, db: Session = Depends(get_db)):
    db_dept = db.query(models.Department).filter(models.Department.Id == department_id).first()
    if db_dept is None:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(db_dept)
    db.commit()
    return db_dept
