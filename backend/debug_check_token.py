
import sys
import os

# Current dir is backend
sys.path.append(os.path.dirname(__file__))

from db import models, database
from sqlalchemy.orm import Session

def check_token(token):
    db: Session = database.SessionLocal()
    try:
        invitation = db.query(models.Invitation).filter(models.Invitation.Token == token).first()
        if not invitation:
            print(f"Token {token} NOT FOUND in DB")
            return

        print(f"Token Found: {invitation.Token}")
        print(f"Email: {invitation.Email}")
        print(f"GoalId: {invitation.GoalId}")
        print(f"QuestionText: {invitation.QuestionText}")
        print(f"Used: {invitation.Used}")
        print(f"ExpiresAt: {invitation.ExpiresAt}")
        
        # Check assignments
        assignments = db.query(models.Assignment)\
            .filter(models.Assignment.GoalId == invitation.GoalId)\
            .filter(models.Assignment.QuestionText == invitation.QuestionText)\
            .all()
            
        print(f"Matching Assignments Count: {len(assignments)}")
        for a in assignments:
            print(f" - Id: {a.Id}, ParentId: {a.ParentAssignmentId}, Text: {a.QuestionText}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    token = "cf0141ab-d5a3-4ac8-921c-f543ea9a1e63"
    check_token(token)
