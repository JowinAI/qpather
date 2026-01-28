from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import models, schemas
from api.dependencies.model_utils import get_db
from datetime import datetime, timezone
from sqlalchemy import func

router = APIRouter()


#Goal First Save with questions
@router.post("/goal/save", response_model=dict)
async def save(goal_payload: schemas.GoalWithAssignments, db: Session = Depends(get_db)):
    try:
        import uuid
        
        goal_thread_id = None
        
        if goal_payload.goal_id:
            # Update existing goal
            goal = db.query(models.Goal).filter(models.Goal.Id == goal_payload.goal_id).first()
            if not goal:
                raise HTTPException(status_code=404, detail="Goal not found")
            
            # Ensure ThreadId exists if it's missing (backfill)
            if not goal.ThreadId:
                goal.ThreadId = str(uuid.uuid4())
            goal_thread_id = goal.ThreadId
            
            goal.Title = goal_payload.title
            goal.GoalDescription = goal_payload.description
            goal.DueDate = goal_payload.due_date
            goal.OrganizationId = goal_payload.organization_id
            goal.DepartmentId = goal_payload.department_id
            
            # Fetch existing assignments
            existing_assignments = db.query(models.Assignment).filter(models.Assignment.GoalId == goal.Id).order_by(models.Assignment.Order).all()
            
            # Update assignments and their user responses
            for idx, question in enumerate(goal_payload.questions):
                if idx < len(existing_assignments):
                    assignment = existing_assignments[idx]
                    assignment.QuestionText = question.text
                    # Backfill ThreadId
                    if not assignment.ThreadId:
                        assignment.ThreadId = goal_thread_id
                else:
                    # Create new assignment if payload has more questions
                    assignment = models.Assignment(
                        GoalId=goal.Id,
                        QuestionText=question.text,
                        Order=idx + 1,
                        CreatedBy=goal_payload.created_by.email,
                        ThreadId=goal_thread_id
                    )
                    db.add(assignment)
                    db.flush() # Get ID
                    db.refresh(assignment)

                # Update User Responses (Assigned Users)
                # Get current assigned users
                current_responses = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == assignment.Id).all()
                current_emails = {r.AssignedTo: r for r in current_responses}
                new_emails = set(u.email for u in question.assigned_users)
                
                # Update existing responses with ThreadId if missing
                for r in current_responses:
                    if not r.ThreadId:
                        r.ThreadId = goal_thread_id
                
                # Add new users
                for user in question.assigned_users:
                    if user.email not in current_emails:
                        new_resp = models.UserResponse(
                            AssignmentId=assignment.Id,
                            AssignedTo=user.email,
                            Status='Assigned',
                            CreatedBy=goal_payload.created_by.email,
                            ThreadId=goal_thread_id
                        )
                        db.add(new_resp)
                
                # Remove unassigned users
                for email, resp in current_emails.items():
                    if email not in new_emails:
                        db.delete(resp)
            
            # Prepare response with assignments
            final_assignments = db.query(models.Assignment).filter(models.Assignment.GoalId == goal.Id).all()
            assignment_list = [{"Id": a.Id, "QuestionText": a.QuestionText} for a in final_assignments]
            
            db.commit()
            return {"goal_id": goal.Id, "assignments": assignment_list}

        else:
            # Insert the Goal and get its ID
            import uuid
            new_thread_id = str(uuid.uuid4())
            
            new_goal = models.Goal(
                OrganizationId=goal_payload.organization_id,
                Title=goal_payload.title,
                DueDate=goal_payload.due_date,
                GoalDescription=goal_payload.description,
                CreatedBy=goal_payload.created_by.email,
                DepartmentId=goal_payload.department_id,
                ThreadId=new_thread_id
            )
            db.add(new_goal)
            db.commit()
            db.refresh(new_goal)
            goal_id = new_goal.Id
    
            created_assignments = []

            for idx, question in enumerate(goal_payload.questions, start=1):
                # Create assignment entry with sequential order
                new_assignment = models.Assignment(
                    GoalId=goal_id,
                    ParentAssignmentId=None,  # Assuming root-level assignments
                    QuestionText=question.text,
                    Order=idx,
                    CreatedBy=goal_payload.created_by.email,
                    ThreadId=new_thread_id
                )
                db.add(new_assignment)
                db.commit()
                db.refresh(new_assignment)
                
                created_assignments.append({"Id": new_assignment.Id, "QuestionText": new_assignment.QuestionText})
    
                # Assign users to assignments
                for user in question.assigned_users:
                    new_user_response = models.UserResponse(
                        AssignmentId=new_assignment.Id,
                        AssignedTo=user.email,
                        Status='Assigned',
                        CreatedBy=goal_payload.created_by.email,
                        ThreadId=new_thread_id
                    )
                    db.add(new_user_response)
                    
                    # Logic to trigger invitation email if user is new/external
                    # Check if user exists in the system (by email)
                    existing_user = db.query(models.User).filter(models.User.Email == user.email).first()
                    
                    # If user does NOT exist, we trigger the invitation email flow
                    if not existing_user:
                        # Create Invitation record (and send email)
                        # We re-use logic similar to `create_invitation` in `invitation.py`, 
                        # but we can't easily call that async route function directly here efficiently without refactoring.
                        # So we implement the core logic here: create DB record + send email.
                        
                        import uuid
                        from datetime import datetime, timedelta
                        from utils.email_service import send_email
                        import os
                        
                        invitation_token = str(uuid.uuid4())
                        # 7 days expiry
                        expires_at = datetime.utcnow() + timedelta(days=7)
                        
                        invitation = models.Invitation(
                            Email=user.email,
                            Token=invitation_token,
                            FirstName=user.name.split(' ')[0] if user.name else '', # Simple assumption
                            LastName=' '.join(user.name.split(' ')[1:]) if user.name and ' ' in user.name else '',
                            Role='Specialist', # Default or passed? Schema doesn't have role on AssignmentUser unfortunately.
                            GoalId=goal_id,
                            QuestionText=question.text,
                            ExpiresAt=expires_at,
                            CreatedBy=goal_payload.created_by.email
                        )
                        db.add(invitation)
                        # We don't commit yet, we commit at the end of loop.
                        
                        # Send Email
                        FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
                        invite_link = f"{FRONTEND_URL}/invitation/{invitation_token}"
                        subject = f"You've been invited to contribute to a goal on DOOE AI"
                        
                        html_body = f"""
                        <html>
                            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                                    <h2 style="color: #2563EB;">Invitation to Contribute</h2>
                                    <p>Hi {invitation.FirstName or 'there'},</p>
                                    <p><strong>{invitation.CreatedBy}</strong> has requested your input on a strategic goal.</p>
                                    
                                    <div style="background-color: #F3F4F6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                        <p style="margin: 0; font-weight: bold;">Question:</p>
                                        <p style="margin: 5px 0 0 0; font-style: italic;">"{invitation.QuestionText}"</p>
                                    </div>

                                    <p>Please click the button below to provide your answer securely.</p>

                                    <div style="text-align: center; margin: 30px 0;">
                                        <a href="{invite_link}" style="background-color: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                                            Respond Now
                                        </a>
                                    </div>
                                    
                                    <p style="font-size: 0.9em; text-align: center; color: #666;">
                                        Link: <a href="{invite_link}">{invite_link}</a>
                                    </p>
                                    
                                    <p style="font-size: 0.8em; color: #888; text-align: center;">
                                        This link will expire in 7 days.
                                    </p>
                                </div>
                            </body>
                        </html>
                        """
                        try:
                            await send_email(subject, [invitation.Email], html_body)
                        except Exception as e:
                            print(f"Failed to send email to {invitation.Email}: {e}")

            db.commit()  # Commit all assignments, responses, and invitations

            # After commit, we should ideally trigger the emails if we can't do it inside transaction easily.
            # But let's try to handle it.
            
            return {"goal_id": goal_id, "assignments": created_assignments}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



# Create a new goal
@router.post("/goal/", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    import uuid
    new_thread_id = str(uuid.uuid4())
    
    new_goal = models.Goal(
        OrganizationId=goal.OrganizationId,
        Title=goal.Title,
        DueDate=goal.DueDate,  # Changed from Date to DueDate
        InitiatedBy=goal.InitiatedBy,
        GoalDescription=goal.GoalDescription,
        CreatedBy=goal.CreatedBy,
        ThreadId=new_thread_id
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

    # Recursive fetch for any assignments that are children of these
    # This ensures we get the full hierarchy even if a child assignment's GoalId was not set correctly
    assignment_ids = {a.Id for a in assignments}
    
    newly_found = True
    while newly_found:
        newly_found = False
        if not assignment_ids:
            break
            
        # Get all children of current set that are NOT in current set
        children = db.query(models.Assignment).filter(
            models.Assignment.ParentAssignmentId.in_(assignment_ids),
            models.Assignment.Id.not_in(assignment_ids)
        ).all()
        
        if children:
            for child in children:
                assignments.append(child)
                assignment_ids.add(child.Id)
            newly_found = True

    assignment_details = []
    for assignment in assignments:
        # Get user responses for each assignment
        user_responses = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == assignment.Id).all()

        # Resolve Names
        emails = [r.AssignedTo for r in user_responses]
        email_name_map = {}
        
        if emails:
            # 1. Check Registered Users
            users = db.query(models.User).filter(models.User.Email.in_(emails)).all()
            for u in users:
                if u.FirstName or u.LastName:
                    email_name_map[u.Email] = f"{u.FirstName or ''} {u.LastName or ''}".strip()
            
            # 2. Check Invitations (for those not found in Users)
            # We filter by GoalId to ensure we get the name used for *this* goal context if possible
            missing_emails = [e for e in emails if e not in email_name_map]
            if missing_emails:
                invites = db.query(models.Invitation).filter(
                    models.Invitation.Email.in_(missing_emails),
                    models.Invitation.GoalId == goal_id 
                ).all()
                for inv in invites:
                     if inv.FirstName or inv.LastName:
                        email_name_map[inv.Email] = f"{inv.FirstName or ''} {inv.LastName or ''}".strip()
                
                # If still missing (maybe invited to other goals?), try global invitation search
                still_missing = [e for e in missing_emails if e not in email_name_map]
                if still_missing:
                     invites_global = db.query(models.Invitation).filter(
                        models.Invitation.Email.in_(still_missing)
                     ).all()
                     for inv in invites_global:
                         if inv.FirstName or inv.LastName:
                            email_name_map[inv.Email] = f"{inv.FirstName or ''} {inv.LastName or ''}".strip()

        user_response_list = [
            schemas.UserResponseDetail(
                AssignedTo=response.AssignedTo,
                Name=email_name_map.get(response.AssignedTo),
                Answer=response.Answer,
                Status=response.Status,
                CreatedAt=response.CreatedAt,
                UpdatedAt=response.UpdatedAt,
                ThreadId=response.ThreadId
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
            ThreadId=assignment.ThreadId,
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
        ThreadId=goal.ThreadId,
        Assignments=assignment_details
    )

# Get all goals
# @router.get("/goal/mygoals", response_model=List[schemas.Goal])
# def get_goals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     goals = db.query(models.Goal).order_by(models.Goal.Id).offset(skip).limit(limit).all()
#     return goals


@router.get("/mygoals", response_model=schemas.PaginatedGoalSummary)
def get_goal_summary(skip: int = 0, limit: int = 100, user_email: str = None, db: Session = Depends(get_db)):
    try:
        print(f"DEBUG: get_goal_summary - skip={skip}, limit={limit}, user_email='{user_email}'")
        
        if not user_email:
            print("DEBUG: No user_email provided, returning empty list")
            return schemas.PaginatedGoalSummary(total=0, items=[])

        # Normalize email for case-insensitive comparison
        email_lower = user_email.lower()
        
        # Build filter criteria
        filter_criteria = [
            (func.lower(models.Goal.CreatedBy) == email_lower)
        ]

        # Base query for goals with distinct count
        base_query = db.query(models.Goal).distinct()
        for criterion in filter_criteria:
            base_query = base_query.filter(criterion)
        
        # Calculate total count
        total_goals = base_query.count()

        # Fetch the actual items with pagination and ordering
        goals = (
            base_query.order_by(models.Goal.CreatedAt.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not goals and total_goals > 0:
             # This might happen if page is out of range, but we just return empty list
             pass 
        
        goal_summary_list = [
            schemas.GoalSummary(
                Id=goal.Id,
                Title=goal.Title,
                DueDate=goal.DueDate.strftime("%Y-%m-%d") if goal.DueDate else "No Due Date",
                Status=(
                    "Completed"
                    if db.query(models.UserResponse)
                       .join(models.Assignment)
                       .filter(models.Assignment.GoalId == goal.Id)
                       .count() > 0 
                       and 
                       db.query(models.UserResponse)
                       .join(models.Assignment)
                       .filter(
                           models.Assignment.GoalId == goal.Id,
                           models.UserResponse.Status != "Completed"
                       ).count() == 0
                    else
                    ("Overdue" if goal.DueDate and goal.DueDate.replace(tzinfo=timezone.utc) < datetime.now().astimezone(timezone.utc)
                    else "In Progress")
                ),
                AssignedUsers=[user.AssignedTo for user in db.query(models.UserResponse.AssignedTo)
                               .join(models.Assignment)
                               .filter(models.Assignment.GoalId == goal.Id)
                               .distinct().all()],
                CreatedBy=goal.CreatedBy,
                ViewLink=f"/goal/details/{goal.Id}"
            ) for goal in goals
        ]

        return schemas.PaginatedGoalSummary(total=total_goals, items=goal_summary_list)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")




# Delete goal by ID
# Delete goal by ID with cascade deletion of related data
@router.delete("/goal/{goal_id}", response_model=schemas.Goal)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    """Delete a goal and all related data (assignments and user responses)."""
    try:
        # First, verify the goal exists
        db_goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()
        if db_goal is None:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Get all assignments for this goal
        assignments = db.query(models.Assignment).filter(models.Assignment.GoalId == goal_id).all()
        assignment_ids = [assignment.Id for assignment in assignments]
        
        # Delete user responses for all assignments
        if assignment_ids:
            db.query(models.UserResponse).filter(
                models.UserResponse.AssignmentId.in_(assignment_ids)
            ).delete(synchronize_session=False)
        
        # Delete invitations for this goal
        db.query(models.Invitation).filter(models.Invitation.GoalId == goal_id).delete(synchronize_session=False)

        # Delete all assignments for this goal
        db.query(models.Assignment).filter(models.Assignment.GoalId == goal_id).delete(synchronize_session=False)
        
        # Store goal data before deletion for response
        goal_data = db_goal
        
        # Finally, delete the goal itself
        db.delete(db_goal)
        
        # Commit all changes
        db.commit()
        return goal_data
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting goal: {str(e)}")
