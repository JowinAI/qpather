from db.database import SessionLocal
from db import models
from sqlalchemy import text

def check_405():
    db = SessionLocal()
    try:
        # Check connection
        print("Checking DB connection...")
        
        # Find Assignment 405
        assignment = db.query(models.Assignment).filter(models.Assignment.Id == 405).first()
        if not assignment:
            print("Assignment 405 NOT FOUND")
            # List some assignments to be sure
            all_a = db.query(models.Assignment).limit(5).all()
            print(f"First 5 Assignments: {[a.Id for a in all_a]}")
        else:
            print(f"Assignment 405 Found: {assignment.QuestionText}")
            
            # Responses attached to 405
            responses = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == 405).all()
            print(f"Responses linked directly to 405 (Parent): {len(responses)}")
            for r in responses:
                print(f" - User: {r.AssignedTo}, Status: {r.Status}, Answer: {r.Answer}")

            # Child Assignments of 405 (Delegations)
            children = db.query(models.Assignment).filter(models.Assignment.ParentAssignmentId == 405).all()
            print(f"Child Assignment (Delegations) of 405: {len(children)}")
            for c in children:
                print(f" - Child ID: {c.Id}, CreatedBy: {c.CreatedBy}")
                child_responses = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == c.Id).all()
                for cr in child_responses:
                    print(f"   -> Response: {cr.AssignedTo}, Answer: {cr.Answer}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_405()
