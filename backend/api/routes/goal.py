from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()


#Goal Save
@router.post("/goals/save", response_model=dict)
def save(goal_payload: schemas.GoalWithAssignments, db: Session = Depends(get_db)):
    try:
        # Insert the Goal and get its ID
        new_goal = models.Goal(
            OrganizationId=goal_payload.organization_id,
            Title=goal_payload.title,
            DueDate=goal_payload.due_date,
            GoalDescription=goal_payload.description,
            CreatedBy=goal_payload.created_by.email,
            DepartmentId=goal_payload.department_id
        )
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        goal_id = new_goal.Id

        for idx, question in enumerate(goal_payload.questions, start=1):
            # Create assignment entry with sequential order
            new_assignment = models.Assignment(
                GoalId=goal_id,
                ParentAssignmentId=None,  # Assuming root-level assignments
                QuestionText=question.text,
                Order=idx,
                CreatedBy=goal_payload.created_by.email
            )
            db.add(new_assignment)
            db.commit()
            db.refresh(new_assignment)

            # Assign users to assignments
            for user in question.assigned_users:
                new_user_response = models.UserResponse(
                    AssignmentId=new_assignment.Id,
                    AssignedTo=user.email,
                    Status='Assigned',
                    CreatedBy=goal_payload.created_by.email
                )
                db.add(new_user_response)

        db.commit()  # Commit all assignments and responses

        return {"goal_id": goal_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
# Create a new goal
@router.post("/goals/", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    new_goal = models.Goal(
        OrganizationId=goal.OrganizationId,
        Title=goal.Title,
        DueDate=goal.DueDate,  # Changed from Date to DueDate
        InitiatedBy=goal.InitiatedBy,
        GoalDescription=goal.GoalDescription,
        CreatedBy=goal.CreatedBy
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

# Get goal by ID
@router.get("/goals/{goal_id}", response_model=schemas.Goal)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

# Get all goals
@router.get("/goals/", response_model=List[schemas.Goal])
def get_goals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    goals = db.query(models.Goal).order_by(models.Goal.Id).offset(skip).limit(limit).all()
    return goals

# Update goal by ID
@router.put("/goals/{goal_id}", response_model=schemas.Goal)
def update_goal(goal_id: int, goal: schemas.GoalUpdate, db: Session = Depends(get_db)):
    db_goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db_goal.OrganizationId = goal.OrganizationId
    db_goal.Title = goal.Title
    db_goal.DueDate = goal.DueDate  # Changed from Date to DueDate
    db_goal.InitiatedBy = goal.InitiatedBy
    db_goal.GoalDescription = goal.GoalDescription
    db_goal.UpdatedBy = goal.UpdatedBy
    db.commit()
    db.refresh(db_goal)
    return db_goal

# Delete goal by ID
@router.delete("/goals/{goal_id}", response_model=schemas.Goal)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    db_goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(db_goal)
    db.commit()
    return db_goal
