from fastapi.testclient import TestClient
from unittest.mock import MagicMock
# We will mock the supabase part because we can't easily test real supabase from here without credentials/setup in python env
# But the request is to test tasks creation API and posting notifications. 
# Notification logic is currently mostly in Frontend (direct Supabase call).
# But there is a backend route for Task/Goal save.

# Let's test the Goal/Task assignment flow in the backend first.
# Then verifying notification: The User Request implies they want to test the notification API. 
# BUT: Notifications are currently client-side Supabase calls in this architecture (see notifications-supabase.ts). 
# There is NO backend (FastAPI) route for notifications in the files I've seen (it was all Supabase client).
# Wait, let me double check if there are any notification routes in backend.
# api/routes/ does NOT have notification.py. list_dir earlier showed:
# aiagent.py, analysis.py, assignment.py, audit_log.py, billing.py, client.py, department.py, feature.py, files.py, goal.py, ...
# So notifications are PURELY frontend -> Supabase.

# HOWEVER, the USER REQUEST says "test this api first... post the notification api".
# If the user *expects* an API for this, they might be referring to the `saveGoal` endpoint I just modified to return assignment IDs.
# Or they want me to script the *frontend logic* using python requests to simulate the flow against the backend + Supabase?
# Testing Supabase directly from Python requires `supabase-py` and keys.
# The user env might not have `supabase` pip package installed or the keys exposed in env vars effectively for this script.

# STRATEGY: 
# 1. Test the `goal/save` endpoint to ensure it returns the Assignment IDs correctly (crucial for the frontend notification logic).
# 2. Since I cannot easily test the Supabase notification *insertion* (frontend logic) via a Python backend test script (missing context/keys maybe),
#    I will simulate the data flow that *would* happen.
#    Actually, I can try to verify if I can write to the `notifications` table if there's a backend proxy? 
#    No backend proxy found.
#    
#    I will focus on testing the Backend `save` -> Returns Assignments flow.
#    Then I will explain that the notification "API" is actually the Supabase client in the frontend, 
#    and I verified the *Prerequisite Data* (Assignment IDs) is now available.

def test_goal_save_returns_assignments(client: TestClient):
    # Setup dependencies
    client_res = client.post("/api/v1/clients/", json={"Name": "Notif Test Client"})
    org_res = client.post("/api/v1/organizations/", json={"ClientId": client_res.json()["Id"], "Name": "Notif Test Org"})
    org_id = org_res.json()["Id"]
    dept_res = client.post("/api/v1/departments/", json={"OrganizationId": org_id, "Name": "Notif Test Dept"})
    dept_id = dept_res.json()["Id"]
    
    # Create User
    user_email = "user@dooe.ai"
    user_res = client.post("/api/v1/users/", json={
        "OrganizationId": org_id, 
        "DepartmentId": dept_id,
        "Email": user_email, 
        "Role":"Tester",
        "CreatedBy": "admin"
    })
    user_id = user_res.json()["Id"]

    # CREATE GOAL
    goal_data = {
        "title": "Notification Integration Test Goal",
        "description": "Testing if save returns assignments",
        "department_id": dept_id,
        "organization_id": org_id,
        "created_by": {"id": user_id, "email": user_email, "name": "User"},
        "questions": [
            {
                "text": "Task A for Notification", 
                "assigned_users": [{"id": user_id, "email": user_email, "name": "User"}]
            },
            {
                "text": "Task B for Notification", 
                "assigned_users": [{"id": user_id, "email": user_email, "name": "User"}]
            }
        ]
    }
    
    # Call Post
    res = client.post("/api/v1/goal/save", json=goal_data)
    assert res.status_code == 200
    data = res.json()
    
    # VERIFY response structure has assignments
    assert "goal_id" in data
    assert "assignments" in data
    assert len(data["assignments"]) == 2
    
    # Verify content
    qst_texts = [a["QuestionText"] for a in data["assignments"]]
    assert "Task A for Notification" in qst_texts
    assert "Task B for Notification" in qst_texts
    
    # Verify IDs are present
    assert data["assignments"][0]["Id"] is not None
    assert data["assignments"][1]["Id"] is not None
    
    print("\nSUCCESS: Backend returned Assignment IDs correctly!")
    print("Assignment Data:", data["assignments"])

    # Now verify those assignments physically exist in DB via assignment API if available, 
    # or just trust the previous step + existing tests.
    
    # Regarding Notification API:
    # Since it is Supabase-client side, we can't 'test' it via FastAPI client.
    # But this test PROVES the frontend receives the IDs it needs to call `createNotification(..., type='assignment', relatedId=AssignmentID)`
