from sqlalchemy.orm import Session
from db import models, database
from sqlalchemy import create_engine

def seed_departments():
    db = database.SessionLocal()
    try:
        # Get the first organization or default to ID 1
        org = db.query(models.Organization).first()
        if not org:
            print("No organization found. Please create an organization first.")
            # For robustness, let's create a default one if none exists
            print("Creating default organization 'Default Org'...")
            # We need a client first?
            client = db.query(models.Client).first()
            if not client:
                 client = models.Client(Name="Default Client", ContactEmail="admin@example.com")
                 db.add(client)
                 db.commit()
                 db.refresh(client)
            
            org = models.Organization(ClientId=client.Id, Name="Default Org", ContactEmail="info@example.com")
            db.add(org)
            db.commit()
            db.refresh(org)
        
        org_id = org.Id
        print(f"Using Organization ID: {org_id}")

        departments_to_add = [
            "Sales",
            "Engineering",
            "Marketing",
            "Development",
            "Management"
        ]

        for dept_name in departments_to_add:
            exists = db.query(models.Department).filter(
                models.Department.OrganizationId == org_id,
                models.Department.Name == dept_name
            ).first()

            if not exists:
                new_dept = models.Department(
                    OrganizationId=org_id,
                    Name=dept_name,
                    ManagerName="System Admin", # Default manager
                    CreatedBy="seed_script"
                )
                db.add(new_dept)
                print(f"Added department: {dept_name}")
            else:
                print(f"Department already exists: {dept_name}")
        
        db.commit()
        print("Department seeding completed.")

    except Exception as e:
        print(f"Error seeding departments: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_departments()
