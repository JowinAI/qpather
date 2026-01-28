import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from db.models import UserResponse, Assignment
from db.database import SessionLocal

# Setup DB connection
db = SessionLocal()

def cleanup_tasks():
    user_email = "user@dooe.ai"
    print(f"Fetching tasks for {user_email}...")
    
    # query user responses
    responses = db.query(UserResponse).filter(UserResponse.AssignedTo == user_email).order_by(UserResponse.CreatedAt.desc()).all()
    
    total = len(responses)
    print(f"Found {total} tasks.")
    
    if total <= 2:
        print("Total tasks are 2 or fewer. No deletions needed.")
        return

    # Keep the 2 most recent ones
    to_keep = responses[:2]
    to_delete = responses[2:]
    
    print(f"Keeping {len(to_keep)} most recent tasks:")
    for r in to_keep:
        print(f" - ID: {r.Id}, AssignmentId: {r.AssignmentId}, CreatedAt: {r.CreatedAt}")

    print(f"\nDeleting {len(to_delete)} older tasks...")
    
    for r in to_delete:
        db.delete(r)
    
    db.commit()
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup_tasks()
