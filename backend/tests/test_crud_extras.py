from fastapi.testclient import TestClient

def test_organization_settings_crud(client: TestClient):
    # Setup: Create initial client and org
    client_data = {"Name": "Settings Test Client"}
    client_res = client.post("/api/v1/clients/", json=client_data)
    assert client_res.status_code == 200
    client_id = client_res.json()["Id"]

    org_data = {"ClientId": client_id, "Name": "Settings Test Org"}
    org_res = client.post("/api/v1/organizations/", json=org_data)
    assert org_res.status_code == 200
    org_id = org_res.json()["Id"]

    # 1. READ Organization details (used in Org Settings Page)
    # The frontend uses /api/v1/organizations/{id}
    res = client.get(f"/api/v1/organizations/{org_id}")
    assert res.status_code == 200
    assert res.json()["Name"] == "Settings Test Org"

    # 2. UPDATE Organization details
    # The frontend uses PUT /api/v1/organizations/{id}
    update_data = {
        "ClientId": client_id,
        "Name": "Updated Org Name",
        "ContactEmail": "updated@org.com",
        "Address": "123 Updated St"
    }
    res = client.put(f"/api/v1/organizations/{org_id}", json=update_data)
    assert res.status_code == 200
    updated_org = res.json()
    assert updated_org["Name"] == "Updated Org Name"
    assert updated_org["ContactEmail"] == "updated@org.com"

    # Verify update persisted
    res = client.get(f"/api/v1/organizations/{org_id}")
    assert res.json()["Name"] == "Updated Org Name"

    # 3. Organization Settings (Specific settings table)
    # Check if this route exists or is used. 
    # Current codebase has api/routes/organization_settings.py but frontend doesn't seem to use it yet.
    # Let's test it anyway to ensure backend coverage.
    
    settings_data = {
        "OrganizationId": org_id,
        "BusinessSector": "Tech",
        "CompanySize": "Medium"
    }
    # Assuming endpoint is /api/v1/organization-settings/ (need to check standard naming)
    # Standard naming in this project seems to be /organizationsettings/ based on other files?
    # Let's check route file first or guess based on pattern.
    # If fails, we know route is missing or named differently.

def test_user_settings_flow(client: TestClient):
    # Setup
    client_res = client.post("/api/v1/clients/", json={"Name": "User Test Client"})
    org_res = client.post("/api/v1/organizations/", json={"ClientId": client_res.json()["Id"], "Name": "User Test Org"})
    org_id = org_res.json()["Id"]
    dept_res = client.post("/api/v1/departments/", json={"OrganizationId": org_id, "Name": "User Test Dept"})
    dept_id = dept_res.json()["Id"]

    user_data = {
        "OrganizationId": org_id,
        "DepartmentId": dept_id,
        "FirstName": "Test",
        "LastName": "User",
        "Email": "settings.test@org.com",
        "Role": "Tester",
        "CreatedBy": "admin"
    }
    user_res = client.post("/api/v1/users/", json=user_data)
    user_id = user_res.json()["Id"]

    # 1. READ User (User Settings Page)
    # Frontend mainly uses localStorage, but effectively it syncs or should sync with backend.
    res = client.get(f"/api/v1/users/{user_id}")
    assert res.status_code == 200
    
    # 2. UPDATE User (User Settings Page - Role, Name)
    # Frontend updates localStorage but effectively calls (or should call) PUT /api/v1/users/{id}
    # Note: frontend code shown only updates localStorage/store, but assuming eventual sync
    
    update_data = {
        "OrganizationId": org_id,
        "DepartmentId": dept_id,
        "FirstName": "UpdatedFirst",
        "LastName": "UpdatedLast",
        "Email": "settings.test@org.com",
        "Role": "Super Tester",
        "UpdatedBy": "self"
    }
    res = client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert res.status_code == 200
    assert res.json()["FirstName"] == "UpdatedFirst"
    assert res.json()["Role"] == "Super Tester"

    # 3. User Settings (Preferences/profile extras)
    # Backend has 'usersettings' table/routes.
    # Test creation/update of these specific settings
    
    user_settings_data = {
        "UserId": user_id,
        "Theme": "Dark", # Hypothetical field based on table
        "Notifications": True
    }
    # Need to verify specific fields in UserSettings model
    # Model has: Role, BusinessObjective, CurrentChallenges, etc.
    
    settings_payload = {
        "UserId": user_id,
        "BusinessObjective": "Efficiency",
        "CurrentChallenges": "Time"
    }
    
    # Try creating user settings
    # Assuming path /api/v1/usersettings/ or similar.
    # Will verify this path in next steps if needed.

def test_full_goal_crud(client: TestClient):
    # Setup
    client_res = client.post("/api/v1/clients/", json={"Name": "Goal Client"})
    org_res = client.post("/api/v1/organizations/", json={"ClientId": client_res.json()["Id"], "Name": "Goal Org"})
    dept_res = client.post("/api/v1/departments/", json={"OrganizationId": org_res.json()["Id"], "Name": "Goal Dept"})
    user_res = client.post("/api/v1/users/", json={
        "OrganizationId": org_res.json()["Id"], 
        "DepartmentId": dept_res.json()["Id"],
        "Email": "goal@test.com", "CreatedBy": "admin"
    })
    
    org_id = org_res.json()["Id"]
    dept_id = dept_res.json()["Id"]
    user_id = user_res.json()["Id"]

    # 1. CREATE (Save)
    goal_data = {
        "title": "CRUD Goal",
        "description": "Initial Desc",
        "department_id": dept_id,
        "organization_id": org_id,
        "created_by": {"id": user_id, "email": "goal@test.com", "name": "User"},
        "questions": [{"text": "Q1", "assigned_users": [{"id": user_id, "email": "goal@test.com", "name": "User"}]}]
    }
    res = client.post("/api/v1/goal/save", json=goal_data)
    assert res.status_code == 200
    goal_id = res.json()["goal_id"]

    # 2. READ (Details)
    res = client.get(f"/api/v1/goal/{goal_id}")
    assert res.status_code == 200
    assert res.json()["Title"] == "CRUD Goal"

    # 3. UPDATE (Save with ID)
    update_data = {
        "goal_id": goal_id,
        "title": "CRUD Goal Updated",
        "description": "Updated Desc",
        "department_id": dept_id,
        "organization_id": org_id,
        "created_by": {"id": user_id, "email": "goal@test.com", "name": "User"},
        "questions": [
            {"text": "Q1 Updated", "assigned_users": [{"id": user_id, "email": "goal@test.com", "name": "User"}]},
            {"text": "Q2 New", "assigned_users": [{"id": user_id, "email": "goal@test.com", "name": "User"}]}
        ]
    }
    res = client.post("/api/v1/goal/save", json=update_data)
    assert res.status_code == 200
    
    # Verify Update
    res = client.get(f"/api/v1/goal/{goal_id}")
    assert res.json()["Title"] == "CRUD Goal Updated"
    assert len(res.json()["Assignments"]) == 2 # Q1 and Q2

    # 4. DELETE
    res = client.delete(f"/api/v1/goal/{goal_id}")
    assert res.status_code == 200
    
    # Verify Delete
    res = client.get(f"/api/v1/goal/{goal_id}")
    assert res.status_code == 404

def test_task_response_flow(client: TestClient):
    # Setup Goal and Assign
    # ... (Re-use setup code or make fixture, simpler to copy-paste for standalone clarity here)
    client_res = client.post("/api/v1/clients/", json={"Name": "Task Client"})
    org_id = client.post("/api/v1/organizations/", json={"ClientId": client_res.json()["Id"], "Name": "Task Org"}).json()["Id"]
    dept_id = client.post("/api/v1/departments/", json={"OrganizationId": org_id, "Name": "Task Dept"}).json()["Id"]
    user_res = client.post("/api/v1/users/", json={
        "OrganizationId": org_id, "DepartmentId": dept_id,
        "Email": "task@test.com", "CreatedBy": "admin"
    })
    user_email = "task@test.com"

    goal_data = {
        "title": "Task Goal",
        "description": "Desc",
        "department_id": dept_id,
        "organization_id": org_id,
        "created_by": {"id": 1, "email": user_email, "name": "User"},
        "questions": [{"text": "Task Q1", "assigned_users": [{"id": 1, "email": user_email, "name": "User"}]}]
    }
    res = client.post("/api/v1/goal/save", json=goal_data)
    goal_id = res.json()["goal_id"]
    
    # Get Assignment ID
    details = client.get(f"/api/v1/goal/{goal_id}").json()
    assignment_id = details["Assignments"][0]["Id"]

    # 1. Get My Tasks
    res = client.get(f"/api/v1/my-tasks/?user_email={user_email}")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) >= 1
    assert tasks[0]["Id"] == assignment_id

    # 3. Submit Response
    response_payload = {
        "AssignmentId": assignment_id,
        "AssignedTo": user_email,
        "Answer": "This is my answer",
        "Status": "Completed",
        "CreatedBy": user_email
    }
    
    # Using POST /api/v1/user-responses/ as found in response.py
    # The route checks for existence and updates if needed, which is good.
    res = client.post("/api/v1/user-responses/", json=response_payload)
    assert res.status_code == 200
    assert res.json()["Answer"] == "This is my answer"
    assert res.json()["Status"] == "Completed"

    # 4. Check Response retrieval
    # Using /api/v1/user-responses/assignment/{assignment_id}?user_email=...
    res = client.get(f"/api/v1/user-responses/assignment/{assignment_id}?user_email={user_email}")
    assert res.status_code == 200
    assert res.json()["Answer"] == "This is my answer"
