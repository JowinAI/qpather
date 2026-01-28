
import sys
import os

# Enable importing from backend
sys.path.append(os.path.dirname(__file__))

from db import models, database
from sqlalchemy.orm import Session

def reset_invitation(token):
    db: Session = database.SessionLocal()
    try:
        invitation = db.query(models.Invitation).filter(models.Invitation.Token == token).first()
        if not invitation:
            print("Invitation not found")
            return

        print(f"Resetting invitation: {token}")
        invitation.Used = False
        
        # Find the response I just created
        # Logic: Assignment -> UserResponse
        # I know the user email and the question text.
        
        # Find the child assignment created (ParentId is not None)
        child_assignments = db.query(models.Assignment)\
            .filter(models.Assignment.GoalId == invitation.GoalId)\
            .filter(models.Assignment.QuestionText == invitation.QuestionText)\
            .filter(models.Assignment.CreatedBy == invitation.CreatedBy)\
            .all()
            
        print(f"Found {len(child_assignments)} assignments with this question.")
        
        for a in child_assignments:
            # Check user responses
            responses = db.query(models.UserResponse)\
                .filter(models.UserResponse.AssignmentId == a.Id)\
                .filter(models.UserResponse.AssignedTo == invitation.Email)\
                .all()
                
            for r in responses:
                if r.Answer == "This is a test answer from curl":
                    print(f"Deleting test response {r.Id} and assignment {a.Id}")
                    db.delete(r)
                    db.delete(a) # Only delete assignment if it was the one holding this specific response?
                    # Be careful deleting assignment if it has other responses?
                    # The assignment was created specifically for this user context usually.
        
        db.commit()
        print("Invitation reset successfully.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Token from previous steps
    token = "cf0141ab-d5a3-4ac8-921c-f543ea9a1e63"
    reset_invitation(token)
