from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from db import models, schemas
from sqlalchemy import func
from api.dependencies.model_utils import get_db

router = APIRouter()


 
# Create a new assignment
@router.post("/assignments/", response_model=schemas.Assignment)
def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db)):
    # Fetch ThreadId from Goal
    goal = db.query(models.Goal).filter(models.Goal.Id == assignment.GoalId).first()
    thread_id = goal.ThreadId if goal else None

    new_assignment = models.Assignment(
        GoalId=assignment.GoalId,
        ParentAssignmentId=assignment.ParentAssignmentId,
        QuestionText=assignment.QuestionText,
        Order=assignment.Order,
        CreatedBy=assignment.CreatedBy,
        ThreadId=thread_id
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

# Create a delegated assignment and assign it to a user
@router.post("/delegate-assignment", response_model=schemas.Assignment)
def create_delegated_assignment(assignment: schemas.DelegatedAssignmentCreate, db: Session = Depends(get_db)):
    # Determine ThreadId (From Parent or Goal)
    thread_id = None
    if assignment.ParentAssignmentId:
        parent = db.query(models.Assignment).filter(models.Assignment.Id == assignment.ParentAssignmentId).first()
        thread_id = parent.ThreadId if parent else None
    
    if not thread_id and assignment.GoalId:
         goal = db.query(models.Goal).filter(models.Goal.Id == assignment.GoalId).first()
         thread_id = goal.ThreadId if goal else None

    # 1. Create the Assignment (Child)
    new_assignment = models.Assignment(
        GoalId=assignment.GoalId,
        ParentAssignmentId=assignment.ParentAssignmentId,
        QuestionText=assignment.QuestionText,
        Order=1, # Default order
        CreatedBy=assignment.CreatedBy,
        ThreadId=thread_id
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    # 2. Create the UserResponse
    new_user_response = models.UserResponse(
        AssignmentId=new_assignment.Id,
        AssignedTo=assignment.AssignedToEmail,
        Status='Assigned',
        CreatedBy=assignment.CreatedBy,
        ThreadId=thread_id
    )
    db.add(new_user_response)
    db.commit()
    
    return new_assignment

# Create multiple assignments and assign them to multiple users
@router.post("/assignments/bulk-with-responses", response_model=schemas.AssignmentsFirstSave)
def create_assignments_with_user_responses(assignments_payload: schemas.AssignmentsFirstSave, db: Session = Depends(get_db)):
    # Insert the Goal and get its ID
    import uuid
    new_thread_id = str(uuid.uuid4())

    new_goal = models.Goal(
        Title=assignments_payload.Goal,
        CreatedBy=assignments_payload.InitiatedBy,
        GoalDescription=assignments_payload.GoalDescription,
        OrganizationId=assignments_payload.OrganizationId,
        ThreadId=new_thread_id
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
            CreatedBy=assignment.CreatedBy,
            ThreadId=new_thread_id
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
                CreatedBy=assignment.CreatedBy,
                ThreadId=new_thread_id
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

# Get child assignments (delegated tasks) by parent assignment ID
# Get child assignments (delegated tasks) by parent assignment ID
@router.get("/assignments/{parent_assignment_id}/delegated")
def get_delegated_assignments(parent_assignment_id: int, db: Session = Depends(get_db)):
    # Join Assignment and UserResponse to fetch everything in one query
    results = (
        db.query(models.Assignment, models.UserResponse)
        .join(models.UserResponse, models.Assignment.Id == models.UserResponse.AssignmentId)
        .filter(models.Assignment.ParentAssignmentId == parent_assignment_id)
        .all()
    )
    
    output = []
    for assignment, response in results:
        output.append({
            "assignmentId": assignment.Id,
            "userId": response.AssignedTo,
            "userName": response.AssignedTo, # Assuming name is same as email for now or needs another join
            "status": response.Status,
            "answer": response.Answer,
            "createdAt": response.CreatedAt.isoformat() if response.CreatedAt else None,
            "updatedAt": response.UpdatedAt.isoformat() if response.UpdatedAt else None
        })
    
    return output

# Delete a delegated assignment and its user responses
@router.delete("/assignments/{assignment_id}/delegated/{user_email}")
def delete_delegated_assignment(assignment_id: int, user_email: str, db: Session = Depends(get_db)):
    from urllib.parse import unquote
    user_email = unquote(user_email)
    
    # Find the child assignment with this parent and for this user
    child_assignments = (
        db.query(models.Assignment)
        .filter(models.Assignment.ParentAssignmentId == assignment_id)
        .all()
    )
    
    deleted_count = 0
    for assignment in child_assignments:
        # Find user responses for this assignment and user
        user_responses = (
            db.query(models.UserResponse)
            .filter(
                models.UserResponse.AssignmentId == assignment.Id,
                models.UserResponse.AssignedTo == user_email
            )
            .all()
        )
        
        if user_responses:
            # Delete user responses
            for response in user_responses:
                db.delete(response)
                deleted_count += 1
            
            # Check if there are any other responses for this assignment
            remaining_responses = (
                db.query(models.UserResponse)
                .filter(models.UserResponse.AssignmentId == assignment.Id)
                .count()
            )
            
            # If no other responses, delete the assignment too
            if remaining_responses == 0:
                db.delete(assignment)
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Delegated assignment not found for this user")
    
    db.commit()
    return {"message": f"Successfully deleted {deleted_count} delegated assignment(s)"}

@router.get("/my-tasks/", response_model=List[schemas.AssignmentWithStatus])
def get_my_tasks(user_email: str, db: Session = Depends(get_db)):
    # 1. Fetch tasks assigned to the current user
    results = (
        db.query(models.Assignment, models.UserResponse.Status, models.UserResponse.Answer)
        .join(models.UserResponse, models.Assignment.Id == models.UserResponse.AssignmentId)
        .filter(func.lower(models.UserResponse.AssignedTo) == user_email.lower())
        .all()
    )
    
    if not results:
        return []

    task_ids = [r[0].Id for r in results]
    
    # 2. Fetch all delegated users for these tasks in one query
    # Find assignments where ParentAssignmentId is in our task_ids
    # Join with UserResponse to get who they are assigned to
    delegations = (
        db.query(models.Assignment.ParentAssignmentId, models.UserResponse.AssignedTo)
        .join(models.UserResponse, models.Assignment.Id == models.UserResponse.AssignmentId)
        .filter(models.Assignment.ParentAssignmentId.in_(task_ids))
        .all()
    )
    
    # Map parent_id -> list of assigned emails
    delegation_map = {}
    for parent_id, assigned_email in delegations:
        if parent_id not in delegation_map:
            delegation_map[parent_id] = []
        delegation_map[parent_id].append(assigned_email)

    tasks = []
    for assignment, status, answer in results:
        # Get delegations for this task from our map
        delegated_users = delegation_map.get(assignment.Id, [])
        
        task_data = schemas.AssignmentWithStatus(
            Id=assignment.Id,
            GoalId=assignment.GoalId,
            ParentAssignmentId=assignment.ParentAssignmentId,
            QuestionText=assignment.QuestionText,
            Order=assignment.Order,
            CreatedAt=assignment.CreatedAt,
            UpdatedAt=assignment.UpdatedAt,
            CreatedBy=assignment.CreatedBy,
            UpdatedBy=assignment.UpdatedBy,
            ThreadId=assignment.ThreadId,
            Status=status,
            Answer=answer,
            DelegatedUsers=delegated_users
        )
        tasks.append(task_data)
        
    return tasks
