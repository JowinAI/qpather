import sys
import os

# Add the script's directory to sys.path to ensure imports work regardless of CWD
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from db.database import SessionLocal
from db import models

def setup_defaults():
    db = SessionLocal()
    try:
        # List all Orgs and Depts
        print("\n--- Listing All Organizations ---")
        orgs = db.query(models.Organization).all()
        for o in orgs:
            print(f"ID: {o.Id}, Name: {o.Name}")

        print("\n--- Listing All Departments ---")
        depts = db.query(models.Department).all()
        for d in depts:
            print(f"ID: {d.Id}, Name: {d.Name}, OrgId: {d.OrganizationId}")


    except Exception as e:
        print(f"Error during setup: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    setup_defaults()
