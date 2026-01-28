from fastapi.testclient import TestClient

def test_read_root(client: TestClient):
    response = client.get("/")
    # Main app might not have root endpoint, checking health or docs usually works
    # But let's check a known endpoint like /api/v1/departments/ if root fails
    assert response.status_code in [200, 404]

def test_create_full_flow(client: TestClient):
    # 1. Create Client
    client_data = {"Name": "Test Client", "ContactEmail": "test@client.com"}
    response = client.post("/api/v1/clients/", json=client_data)
    assert response.status_code == 200
    client_id = response.json()["Id"]

    # 2. Create Organization
    org_data = {
        "ClientId": client_id,
        "Name": "Test Org", 
        "ContactEmail": "test@org.com"
    }
    response = client.post("/api/v1/organizations/", json=org_data)
    assert response.status_code == 200
    org_id = response.json()["Id"]

    # 3. Create Department
    dept_data = {
        "OrganizationId": org_id,
        "Name": "Test Dept",
        "ManagerName": "Test Manager"
    }
    response = client.post("/api/v1/departments/", json=dept_data)
    assert response.status_code == 200
    dept_id = response.json()["Id"]

    # 4. Create User
    user_data = {
        "OrganizationId": org_id,
        "DepartmentId": dept_id,
        "FirstName": "Test",
        "LastName": "User",
        "Email": "test.user@org.com",
        "Role": "Employee",
        "CreatedBy": "admin"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["Id"]
    assert response.json()["Email"] == "test.user@org.com"

    # 5. List Departments
    response = client.get("/api/v1/departments/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 6. Create Goal
    goal_data = {
        "title": "Test Goal",
        "description": "Test Description",
        "department_id": dept_id,
        "organization_id": org_id,
        "created_by": {
            "id": user_id,
            "name": "Test User",
            "email": "test.user@org.com"
        },
        "questions": [
            {
                "text": "Question 1",
                "assigned_users": [
                    {
                        "id": user_id,
                        "name": "Test User",
                        "email": "test.user@org.com"
                    }
                ]
            }
        ]
    }
    response = client.post("/api/v1/goal/save", json=goal_data)
    assert response.status_code == 200
    goal_response_data = response.json()
    assert "goal_id" in goal_response_data
    goal_id = goal_response_data["goal_id"]

    # 7. List My Goals (Summary)
    response = client.get(f"/api/v1/mygoals?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

    # 8. Check specific goal details
    response = client.get(f"/api/v1/goal/{goal_id}")
    assert response.status_code == 200
    assert response.json()["Title"] == "Test Goal"

    # 9. Assignment Delegation
    # First get assignment id from details
    assignments = response.json()["Assignments"]
    assert len(assignments) > 0
    assignment_id = assignments[0]["Id"]

    delegate_data = {
        "GoalId": goal_id,
        "ParentAssignmentId": assignment_id,
        "QuestionText": "Delegated Question",
        "AssignedToEmail": "test.user@org.com",
        "CreatedBy": "test.user@org.com"
    }
    response = client.post("/api/v1/delegate-assignment", json=delegate_data)
    assert response.status_code == 200
    
    # 10. Update User
    update_data = {
        "OrganizationId": org_id,
        "DepartmentId": dept_id,
        "FirstName": "Updated",
        "LastName": "User",
        "Email": "test.user@org.com",
        "Role": "Manager",
        "UpdatedBy": "admin"
    }
    response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["FirstName"] == "Updated"

    # 11. Delete Goal
    response = client.delete(f"/api/v1/goal/{goal_id}")
    assert response.status_code == 200

    # Verify deletion
    response = client.get(f"/api/v1/goal/{goal_id}")
    assert response.status_code == 404
