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
# Create multiple assignments and assign them to multiple users
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from db import models, schemas
from api.dependencies.model_utils import get_db

router = APIRouter()

# Create multiple assignments and assign them to multiple users
@router.post("/assignments/bulk-with-responses", response_model=schemas.AssignmentsFirstSave)
def create_assignments_with_user_responses(assignments_payload: schemas.AssignmentsFirstSave, db: Session = Depends(get_db)):
    # Insert the Goal and get its ID
    new_goal = models.Goal(
        Title=assignments_payload.Goal,
        CreatedBy=assignments_payload.InitiatedBy,
        GoalDescription=assignments_payload.GoalDescription,
        OrganizationId=assignments_payload.OrganizationId
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    goal_id = new_goal.Id

    new_assignments = []

    for assignment in assignments_payload.Assignments:
        # Create the assignment with the inserted GoalId
        new_assignment = models.Assignment(
            GoalId=goal_id,  # Use the newly created GoalId
            ParentAssignmentId=assignment.ParentAssignmentId,
            QuestionText=assignment.QuestionText,
            Order=assignment.Order,
            CreatedBy=assignment.CreatedBy
        )
        db.add(new_assignment)
        db.commit()  # Commit the assignment to get the AssignmentId
        db.refresh(new_assignment)

        assigned_users = []

        # Assign the assignment to multiple users in the UserResponse table
        for user_email in assignment.AssignedUsers:
            new_user_response = models.UserResponse(
                AssignmentId=new_assignment.Id,
                AssignedTo=user_email,
                Status='Assigned',  # Default to 'Assigned'
                CreatedBy=assignment.CreatedBy
            )
            db.add(new_user_response)
            assigned_users.append(user_email)  # Collect the user email for the response

        new_assignments.append({
            "assignment": new_assignment,
            "assigned_users": assigned_users  # Add assigned users to each assignment
        })

    db.commit()  # Commit all the records at once for both Assignment and UserResponse

    # Prepare the response that includes assignments and the list of assigned users
    response = []
    for entry in new_assignments:
        assignment = entry["assignment"]
        assigned_users = entry["assigned_users"]
        assignment_with_users = schemas.AssignmentWithUsers(
            Id=assignment.Id,
            GoalId=assignment.GoalId,
            ParentAssignmentId=assignment.ParentAssignmentId,
            QuestionText=assignment.QuestionText,
            Order=assignment.Order,
            CreatedAt=assignment.CreatedAt,
            UpdatedAt=assignment.UpdatedAt,
            CreatedBy=assignment.CreatedBy,
            UpdatedBy=assignment.UpdatedBy,
            AssignedUsers=assigned_users  # Add assigned users in the response
        )
        response.append(assignment_with_users)

    return {"Goal": assignments_payload.Goal, "Assignments": response,}

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
