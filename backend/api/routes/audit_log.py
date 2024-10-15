from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create a new audit log entry
@router.post("/audit-log/", response_model=schemas.AuditLog)
def create_audit_log(audit_log: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    new_audit_log = models.AuditLog(
        UserId=audit_log.UserId,
        OrganizationId=audit_log.OrganizationId,
        Action=audit_log.Action
    )
    db.add(new_audit_log)
    db.commit()
    db.refresh(new_audit_log)
    return new_audit_log

# Get audit log by ID
@router.get("/audit-log/{audit_log_id}", response_model=schemas.AuditLog)
def get_audit_log(audit_log_id: int, db: Session = Depends(get_db)):
    audit_log = db.query(models.AuditLog).filter(models.AuditLog.Id == audit_log_id).first()
    if audit_log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return audit_log

# Get all audit log entries
@router.get("/audit-log/", response_model=List[schemas.AuditLog])
def get_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    audit_logs = db.query(models.AuditLog).order_by(models.AuditLog.Timestamp).offset(skip).limit(limit).all()
    return audit_logs


# Update audit log by ID
@router.put("/audit-log/{audit_log_id}", response_model=schemas.AuditLog)
def update_audit_log(audit_log_id: int, audit_log: schemas.AuditLog, db: Session = Depends(get_db)):
    db_audit_log = db.query(models.AuditLog).filter(models.AuditLog.Id == audit_log_id).first()
    if db_audit_log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    db_audit_log.UserId = audit_log.UserId
    db_audit_log.OrganizationId = audit_log.OrganizationId
    db_audit_log.Action = audit_log.Action
    db.commit()
    db.refresh(db_audit_log)
    return db_audit_log

# Delete audit log by ID
@router.delete("/audit-log/{audit_log_id}", response_model=schemas.AuditLog)
def delete_audit_log(audit_log_id: int, db: Session = Depends(get_db)):
    db_audit_log = db.query(models.AuditLog).filter(models.AuditLog.Id == audit_log_id).first()
    if db_audit_log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    db.delete(db_audit_log)
    db.commit()
    return db_audit_log
