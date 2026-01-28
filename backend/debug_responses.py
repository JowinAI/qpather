import sys
import os

# Add the script's directory to sys.path to ensure imports work regardless of CWD
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from db.database import SessionLocal
from db import models

def debug_user_responses():
    db = SessionLocal()
    try:
        print("\n--- User Responses ---")
        responses = db.query(models.UserResponse).all()
        for r in responses:
            print(f"AssignID: {r.AssignmentId}, AssignedTo: {r.AssignedTo}, Status: {r.Status}")

        print("\n--- Assignments ---")
        assignments = db.query(models.Assignment).all()
        for a in assignments:
            print(f"ID: {a.Id}, Text: {a.QuestionText}, Parent: {a.ParentAssignmentId}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_user_responses()
