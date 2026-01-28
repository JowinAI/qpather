from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import os
from db import models, schemas
from api.dependencies.model_utils import get_db
from utils.email_service import send_email
from pydantic import BaseModel

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
INVITATION_EXPIRY_DAYS = 7

class EnhanceRequest(BaseModel):
    text: str

@router.post("/invitations/", response_model=schemas.Invitation)
async def create_invitation(invitation_req: schemas.InvitationCreate, db: Session = Depends(get_db)):
    # Proceed with creation of invitation record regardless, to support the specific flow.
    
    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=INVITATION_EXPIRY_DAYS)
    
    invitation = models.Invitation(
        Email=invitation_req.Email,
        Token=token,
        FirstName=invitation_req.FirstName,
        LastName=invitation_req.LastName,
        Role=invitation_req.Role,
        GoalId=invitation_req.GoalId,
        QuestionText=invitation_req.QuestionText,
        ExpiresAt=expires_at,
        CreatedBy=invitation_req.CreatedBy
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # Send Email
    invite_link = f"{FRONTEND_URL}/invitation/{token}"
    
    subject = f"You've been invited to contribute to a goal on DOOE AI"
    
    # Simple HTML Template
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
                    This link will expire in {INVITATION_EXPIRY_DAYS} days.
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        await send_email(subject, [invitation.Email], html_body)
    except Exception as e:
        print(f"Failed to send email: {e}")
        # We don't fail the request, but log it.
        
    return invitation

@router.get("/invitations/")
def get_invitations(created_by: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Invitation)
    if created_by:
        query = query.filter(models.Invitation.CreatedBy == created_by)
    invitations = query.all()
    
    results = []
    for inv in invitations:
        inv_dict = {
            "Id": inv.Id,
            "Email": inv.Email,
            "Token": inv.Token,
            "FirstName": inv.FirstName,
            "LastName": inv.LastName,
            "Role": inv.Role,
            "GoalId": inv.GoalId,
            "QuestionText": inv.QuestionText,
            "ExpiresAt": inv.ExpiresAt,
            "Used": inv.Used,
            "CreatedAt": inv.CreatedAt,
            "CreatedBy": inv.CreatedBy,
            "AssignmentId": 0 # Default
        }
        
        # Look up Assignment
        # We need to find the assignment related to this question.
        # Ideally, we find a Parent assignment if possible, or just the assignment itself.
        assignment = db.query(models.Assignment)\
            .filter(models.Assignment.GoalId == inv.GoalId)\
            .filter(models.Assignment.QuestionText == inv.QuestionText)\
            .first()
            
        if assignment:
            inv_dict["AssignmentId"] = assignment.Id
            
        results.append(inv_dict)
        
    return results

@router.get("/invitations/{token}")
def get_invitation_context(token: str, db: Session = Depends(get_db)):
    invitation = db.query(models.Invitation).filter(models.Invitation.Token == token).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
        
    if invitation.Used:
        raise HTTPException(status_code=400, detail="This invitation has already been used.")
        
    if invitation.ExpiresAt < datetime.utcnow():
        raise HTTPException(status_code=400, detail="This invitation has expired.")

    # Fetch Goal details for context
    goal = db.query(models.Goal).filter(models.Goal.Id == invitation.GoalId).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    return {
        "invitation": invitation,
        "goal": {
            "Title": goal.Title,
            "Description": goal.GoalDescription
        }
    }

class AnswerRequest(BaseModel):
    AssignmentId: int
    AssignedTo: str
    Answer: str

@router.post("/invitations/{token}/answer")
def submit_invitation_answer(token: str, answer_data: AnswerRequest, db: Session = Depends(get_db)):
    invitation = db.query(models.Invitation).filter(models.Invitation.Token == token).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    # Find matching assignment context (Any matching question in this goal)
    parent_assignment = db.query(models.Assignment)\
        .filter(models.Assignment.GoalId == invitation.GoalId)\
        .filter(models.Assignment.QuestionText == invitation.QuestionText)\
        .first() 
        
    if not parent_assignment:
        raise HTTPException(status_code=404, detail="Original assignment context not found")

    # Check if a child assignment (delegation) already exists for this user
    # We look for an assignment that is a child of parent_assignment 
    # AND has a UserResponse for this email
    existing_delegation = (
        db.query(models.Assignment)
        .join(models.UserResponse, models.Assignment.Id == models.UserResponse.AssignmentId)
        .filter(models.Assignment.ParentAssignmentId == parent_assignment.Id)
        .filter(models.UserResponse.AssignedTo == invitation.Email)
        .first()
    )

    if existing_delegation:
        # Update existing response
        user_response = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == existing_delegation.Id).first()
        if user_response:
            user_response.Answer = answer_data.Answer
            user_response.Status = 'Completed'
            user_response.UpdatedBy = invitation.Email
            user_response.UpdatedAt = datetime.utcnow()
    else:
        # Create NEW Child Assignment (Delegation)
        new_assignment = models.Assignment(
            GoalId=invitation.GoalId,
            ParentAssignmentId=parent_assignment.Id,
            QuestionText=invitation.QuestionText,
            Order=1,
            CreatedBy=invitation.CreatedBy, # The Inviter created the delegation context
            ThreadId=parent_assignment.ThreadId
        )
        db.add(new_assignment)
        db.commit()
        db.refresh(new_assignment)

        # Create UserResponse
        new_user_response = models.UserResponse(
            AssignmentId=new_assignment.Id,
            AssignedTo=invitation.Email,
            Status='Completed',
            Answer=answer_data.Answer,
            CreatedBy=invitation.Email, # The Invitee created the response
            ThreadId=parent_assignment.ThreadId
        )
        db.add(new_user_response)
        
    invitation.Used = True
    db.commit()
    
    return {"message": "Answer submitted successfully"}

@router.post("/invitations/{token}/enhance")
def enhance_answer_with_ai(token: str, request: EnhanceRequest, db: Session = Depends(get_db)):
    # Retrieve invitation to understand the user's role/context if possible
    invitation = db.query(models.Invitation).filter(models.Invitation.Token == token).first()
    
    role = invitation.Role if invitation and invitation.Role else "Specialist"
    original_text = request.text
    
    # Simulate sophisticated AI Enhancement logic
    # In production, this would use an LLM with a prompt like:
    # "Rewrite this text to be more professional, concise, and strategic given the user's role as {role}."
    
    enhanced_text = original_text.strip()
    
    # 1. Capitalization & Punctuation
    if enhanced_text and not enhanced_text[0].isupper():
        enhanced_text = enhanced_text[0].upper() + enhanced_text[1:]
    if enhanced_text and enhanced_text[-1] not in ['.', '!', '?']:
        enhanced_text += '.'
        
    # 2. Professional Vocabulary Expansion (Simulation)
    replacements = {
        "good": "exceptional",
        "bad": "suboptimal",
        "fix": "remediate",
        "change": "optimize",
        "help": "facilitate",
        "need": "require",
        "use": "leverage",
        "fast": "expedited",
        "slow": "gradual",
        "problem": "challenge",
        "think": "believe",
        "make sure": "ensure",
        "job": "responsibility",
        "money": "capital",
        "idea": "initiative",
        "start": "initiate",
        "stop": "cease",
        "buy": "acquire",
        "sell": "divest",
        "happy": "satisfied"
    }
    
    # Apply replacements case-insensitively but preserving case match roughly
    for old, new in replacements.items():
        import re
        # Regex to replace whole words only
        enhanced_text = re.sub(r'\b' + re.escape(old) + r'\b', new, enhanced_text, flags=re.IGNORECASE)
        
    # 3. Role-based prefixing/framing (Simulation)
    # If the text is very short, expand it slightly to sound more complete
    if len(enhanced_text.split()) < 5:
        enhanced_text = f"From a strategic perspective, {enhanced_text.lower()}"
        # corrective capitalization after prefix assignment
        if enhanced_text.startswith("From a strategic perspective, i"):
             enhanced_text = enhanced_text.replace(", i", ", I")
        elif enhanced_text[0].islower():
             enhanced_text = enhanced_text[0].upper() + enhanced_text[1:]

    return {"enhanced_text": enhanced_text}
