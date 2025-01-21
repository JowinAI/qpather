from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db
from datetime import datetime, timezone

router = APIRouter()


#Goal First Save with questions
@router.post("/goal/save", response_model=dict)
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
@router.post("/goal/", response_model=schemas.Goal)
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
@router.get("/goal/{goal_id}", response_model=schemas.GoalDetailsResponse)
def get_goal_details(goal_id: int, db: Session = Depends(get_db)):
    # Retrieve goal details
    goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Get first-level assignments for the goal
    assignments = db.query(models.Assignment).filter(models.Assignment.GoalId == goal_id).all()

    assignment_details = []
    for assignment in assignments:
        # Get user responses for each assignment
        user_responses = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == assignment.Id).all()

        user_response_list = [
            schemas.UserResponseDetail(
                AssignedTo=response.AssignedTo,
                Answer=response.Answer,
                Status=response.Status,
                CreatedAt=response.CreatedAt,
                UpdatedAt=response.UpdatedAt
            ) for response in user_responses
        ]

        assignment_details.append(schemas.AssignmentDetails(
            Id=assignment.Id,
            ParentAssignmentId=assignment.ParentAssignmentId,
            QuestionText=assignment.QuestionText,
            Order=assignment.Order,
            CreatedAt=assignment.CreatedAt,
            UpdatedAt=assignment.UpdatedAt,
            CreatedBy=assignment.CreatedBy,
            UpdatedBy=assignment.UpdatedBy,
            UserResponses=user_response_list
        ))

    return schemas.GoalDetailsResponse(
        Id=goal.Id,
        Title=goal.Title,
        DueDate=goal.DueDate,
        GoalDescription=goal.GoalDescription,
        CreatedAt=goal.CreatedAt,
        UpdatedAt=goal.UpdatedAt,
        CreatedBy=goal.CreatedBy,
        UpdatedBy=goal.UpdatedBy,
        Assignments=assignment_details
    )

# Get all goals
# @router.get("/goal/mygoals", response_model=List[schemas.Goal])
# def get_goals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     goals = db.query(models.Goal).order_by(models.Goal.Id).offset(skip).limit(limit).all()
#     return goals
@router.get("/mygoals", response_model=List[schemas.GoalSummary])
def get_goal_summary(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        # Query to get goals with their assignments and responses
        goals = (
            db.query(models.Goal)
            .outerjoin(models.Assignment, models.Goal.Id == models.Assignment.GoalId)
            .outerjoin(models.UserResponse, models.Assignment.Id == models.UserResponse.AssignmentId)
            .order_by(models.Goal.Id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        if not goals:
            raise HTTPException(status_code=404, detail="No goals found")

        goal_summary_list = []

        for goal in goals:
            # Determine due date display
            due_date_str = goal.DueDate.strftime("%Y-%m-%d") if goal.DueDate else "No Due Date"

            # Gather assigned users for first-level assignments
            assigned_users = db.query(models.UserResponse.AssignedTo).join(models.Assignment).filter(
                models.Assignment.GoalId == goal.Id
            ).distinct().all()

            assigned_user_list = [user.AssignedTo for user in assigned_users]

            # Create the goal summary response
            goal_summary_list.append(schemas.GoalSummary(
                Id=goal.Id,
                Title=goal.Title,
                DueDate=due_date_str,
                Status="In Progress" if goal.DueDate and goal.DueDate > datetime.now(timezone.utc)  else "Overdue",
                AssignedUsers=assigned_user_list,
                ViewLink=f"/goal/details/{goal.Id}"
            ))

        return goal_summary_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

#Update goal by ID
@router.put("/goal/{goal_id}", response_model=schemas.Goal)
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
@router.delete("/goal/{goal_id}", response_model=schemas.Goal)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    db_goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(db_goal)
    db.commit()
    return db_goal
