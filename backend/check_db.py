from db.database import SessionLocal
from db import models

def check_db():
    db = SessionLocal()
    try:
        orgs = db.query(models.Organization).all()
        depts = db.query(models.Department).all()
        users = db.query(models.User).all()
        print(f"Orgs: {[o.Id for o in orgs]}")
        print(f"Depts: {[d.Id for d in depts]}")
        print(f"Users: {[u.Email for u in users]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
