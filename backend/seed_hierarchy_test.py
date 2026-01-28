
import os
import sys
from datetime import datetime
import uuid

# Add backend directory to path
sys.path.append("/Users/joisejoy/Documents/jowinai/qpather/backend")

from db.database import SessionLocal
from db import models

def seed_complex_hierarchy():
    db = SessionLocal()
    try:
        print("--- Seeding Complex Hierarchy Test ---")
        
        # 1. Create a Goal
        thread_id = str(uuid.uuid4())
        goal = models.Goal(
            OrganizationId=1,
            Title="Hierarchy Visibility Test Goal 001",
            GoalDescription="Testing multi-level delegation visibility",
            CreatedBy="admin@dooe.ai", # User 1
            CreatedAt=datetime.now(),
            ThreadId=thread_id
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        print(f"Created Goal: {goal.Id} - {goal.Title}")
        
        # 2. Level 1 Assignment (Admin -> Manager)
        l1_assignment = models.Assignment(
            GoalId=goal.Id,
            QuestionText="L1: High Level Strategy",
            Order=1,
            CreatedBy="admin@dooe.ai", # Created by User 1
            ThreadId=thread_id
        )
        db.add(l1_assignment)
        db.commit()
        db.refresh(l1_assignment)
        
        l1_response = models.UserResponse(
            AssignmentId=l1_assignment.Id,
            AssignedTo="manager@dooe.ai", # User 2
            Status="In Progress",
            Answer="L1 Accepted. Delegating execution.",
            CreatedBy="admin@dooe.ai",
            ThreadId=thread_id
        )
        db.add(l1_response)
        db.commit()
        print(f"  Created L1 Assignment {l1_assignment.Id} for manager@dooe.ai")

        # 3. Level 2 Assignment (Manager -> Lead) - Delegated
        l2_assignment = models.Assignment(
            GoalId=goal.Id,
            ParentAssignmentId=l1_assignment.Id,
            QuestionText="L2: Operational Plan",
            Order=1,
            CreatedBy="manager@dooe.ai", # Created by User 2
            ThreadId=thread_id
        )
        db.add(l2_assignment)
        db.commit()
        db.refresh(l2_assignment)

        l2_response = models.UserResponse(
            AssignmentId=l2_assignment.Id,
            AssignedTo="lead@dooe.ai", # User 3
            Status="In Progress",
            Answer="L2 Plan drafted. Assigning tasks.",
            CreatedBy="manager@dooe.ai",
            ThreadId=thread_id
        )
        db.add(l2_response)
        db.commit()
        print(f"    Created L2 Assignment {l2_assignment.Id} for lead@dooe.ai (Creator: manager@dooe.ai)")

        # 4. Level 3 Assignment (Lead -> Dev 1) - Delegated
        l3_assignment_1 = models.Assignment(
            GoalId=goal.Id,
            ParentAssignmentId=l2_assignment.Id,
            QuestionText="L3: Backend Implementation",
            Order=1,
            CreatedBy="lead@dooe.ai", # Created by User 3
            ThreadId=thread_id
        )
        db.add(l3_assignment_1)
        db.commit()
        db.refresh(l3_assignment_1)

        l3_response_1 = models.UserResponse(
            AssignmentId=l3_assignment_1.Id,
            AssignedTo="dev1@dooe.ai", # User 6
            Status="Completed",
            Answer="API endpoints done.",
            CreatedBy="lead@dooe.ai",
            ThreadId=thread_id
        )
        db.add(l3_response_1)
        db.commit()
        print(f"      Created L3 Assignment {l3_assignment_1.Id} for dev1@dooe.ai (Creator: lead@dooe.ai)")

        # 5. Level 3 Assignment (Lead -> Dev 2) - Delegated
        l3_assignment_2 = models.Assignment(
            GoalId=goal.Id,
            ParentAssignmentId=l2_assignment.Id,
            QuestionText="L3: Frontend Implementation",
            Order=2,
            CreatedBy="lead@dooe.ai", # Created by User 3
            ThreadId=thread_id
        )
        db.add(l3_assignment_2)
        db.commit()
        db.refresh(l3_assignment_2)

        l3_response_2 = models.UserResponse(
            AssignmentId=l3_assignment_2.Id,
            AssignedTo="dev2@dooe.ai", # User 7
            Status="Assigned",
            Answer=None,
            CreatedBy="lead@dooe.ai",
            ThreadId=thread_id
        )
        db.add(l3_response_2)
        db.commit()
        print(f"      Created L3 Assignment {l3_assignment_2.Id} for dev2@dooe.ai (Creator: lead@dooe.ai)")
        
        print(f"\nSUCCESS: Created Hierarchy Test Goal ID: {goal.Id}")
        print("You can verify this by logging in as 'admin@dooe.ai' and viewing the goal.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_complex_hierarchy()
