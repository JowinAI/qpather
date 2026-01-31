import sys
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

# Add verify_goal_response.py directory to path so imports work
sys.path.append(os.getcwd())

from main import app
from db.models import Base
from api.dependencies.model_utils import get_db

# Setup in-memory DB
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def run_check():
    print("Setting up data (Client, Org, Dept, User)...")
    # 1. Create Client
    client_res = client.post("/api/v1/clients/", json={"Name": "Test Client"})
    if client_res.status_code != 200:
        print(f"Failed to create client: {client_res.text}")
        return
    client_id = client_res.json()["Id"]

    # 2. Create Organization
    org_res = client.post("/api/v1/organizations/", json={"Name": "Test Org", "ClientId": client_id})
    if org_res.status_code != 200:
        print(f"Failed to create org: {org_res.text}")
        return
    org_id = org_res.json()["Id"]

    # 3. Create Department
    dept_res = client.post("/api/v1/departments/", json={"Name": "Engineering", "OrganizationId": org_id})
    if dept_res.status_code != 200:
        print(f"Failed to create dept: {dept_res.text}")
        return
    dept_id = dept_res.json()["Id"]

    # 4. Create User
    user_res = client.post("/api/v1/users/", json={
        "Email": "test@dooe.ai",
        "FirstName": "Test",
        "LastName": "User",
        "OrganizationId": org_id,
        "DepartmentId": dept_id,
        "AuthId": "auth_123",
        "CreatedBy": "system"
    })
    if user_res.status_code != 200:
        print(f"Failed to create user: {user_res.text}")
        return
    user_id = user_res.json()["Id"]
    user_email = user_res.json()["Email"]
    user_name = "Test User"

    # 5. Create Goal
    # Construct payload matching GoalWithAssignments schema Test
    user_obj = {"id": user_id, "name": user_name, "email": user_email}
    
    goal_payload = {
        "title": "My Goal Title",
        "description": "Launch Notifications",
        "department_id": dept_id,
        "organization_id": org_id,
        "created_by": user_obj, 
        "questions": [
            {
                "text": "Task A",
                "assigned_users": [user_obj]
            },
            {
                "text": "Task B",
                "assigned_users": [user_obj]
            }
        ]
    }
    
    print("\nSending Goal Payload...")
    response = client.post("/api/v1/goal/save", json=goal_payload)
    
    print("\n--- API RESPONSE ---")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    run_check()
