from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db import models

def seed_data():
    db = SessionLocal()
    try:
        # Check if data exists
        if db.query(models.User).first():
            print("Data already exists. Skipping seed.")
            return

        print("Seeding data...")

        # 1. Client
        client = models.Client(Name="Dooe Client", CreatedBy="Seed")
        db.add(client)
        db.commit()
        db.refresh(client)

        # 2. Organization
        org = models.Organization(ClientId=client.Id, Name="Dooe Corp", CreatedBy="Seed")
        db.add(org)
        db.commit()
        db.refresh(org)

        # 3. Department
        dept = models.Department(OrganizationId=org.Id, Name="Engineering", CreatedBy="Seed")
        db.add(dept)
        db.commit()
        db.refresh(dept)

        # 4. Users
        users = [
            models.User(
                OrganizationId=org.Id,
                DepartmentId=dept.Id,
                FirstName="Alice",
                LastName="Admin",
                Email="alice@dooe.ai",
                Role="Admin",
                CreatedBy="Seed"
            ),
            models.User(
                OrganizationId=org.Id,
                DepartmentId=dept.Id,
                FirstName="Bob",
                LastName="Manager",
                Email="bob@dooe.ai",
                Role="Manager",
                CreatedBy="Seed"
            ),
            models.User(
                OrganizationId=org.Id,
                DepartmentId=dept.Id,
                FirstName="Charlie",
                LastName="Dev",
                Email="charlie@dooe.ai",
                Role="Contributor",
                CreatedBy="Seed"
            ),
             models.User(
                OrganizationId=org.Id,
                DepartmentId=dept.Id,
                FirstName="David",
                LastName="Dev",
                Email="david@dooe.ai",
                Role="Contributor",
                CreatedBy="Seed"
            )
        ]
        db.add_all(users)
        db.commit()
        
        print("Seeding completed successfully!")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
