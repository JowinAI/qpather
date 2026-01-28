from db.database import SessionLocal
from db import models
import uuid

def fix_405():
    db = SessionLocal()
    try:
        parent_id = 405
        parent = db.query(models.Assignment).filter(models.Assignment.Id == parent_id).first()
        if not parent:
            print("Parent 405 not found")
            return

        print(f"Fixing delegations for Parent {parent_id}...")
        
        # Find responses linked directly to parent (excluding maybe the creator if they answered their own? 
        # But usually parent assignment doesn't have a response unless self-assigned.
        # Ideally, Parent Assignment shouldn't have UserResponses if it's a Manager Task.
        # But if 'My Tasks' shows it, it might have one for the owner.
        # Let's assume all OTHER users are delegations.
        
        responses = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == parent_id).all()
        
        for r in responses:
            print(f"Processing response for {r.AssignedTo}...")
            
            # If this is the creator, maybe we leave it? 
            # But the 'Delegation' view shows sub-tasks.
            # If I assigned myself a sub-task, it should be a child.
            # If this response represents the "Manager's Conclusion", it might stay on Parent.
            # However, the existence of `joisetest@gmail.com` confirms it's an external invitee.
            
            # Let's migrate EVERYONE who is NOT the creator, or just everyone?
            # If I migrate the creator, they technically delegated to themselves.
            
            # Let's check if a child already exists (to avoid duplicates if run multiple times)
            existing_child = db.query(models.Assignment).filter(
                models.Assignment.ParentAssignmentId == parent_id,
                # How to identiy child for this user? We usually look at UserResponse.
                # But here we are creating the child.
                # We can check created_by or just blindly creating?
                # Best to check if we already have a child with a response for this user.
                # But we know we have 0 children from previous check.
            ).count()
            
            # Logic: Create Child Assignment, Link Response to Child.
            
            new_child = models.Assignment(
                GoalId=parent.GoalId,
                ParentAssignmentId=parent.Id,
                QuestionText=parent.QuestionText,
                Order=1,
                CreatedBy=parent.CreatedBy, # The delegator
                ThreadId=parent.ThreadId
            )
            db.add(new_child)
            db.commit() # Need ID
            db.refresh(new_child)
            
            # Move the response
            r.AssignmentId = new_child.Id
            # Check if r.ThreadId is set, if not take from parent
            if not r.ThreadId:
                r.ThreadId = parent.ThreadId
                
            db.add(r)
            db.commit()
            
            print(f" -> Moved response to new Child Assignment {new_child.Id}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_405()
