from sqlalchemy.orm import Session
from db import models, database

def remove_duplicate_sales():
    db = database.SessionLocal()
    try:
        # Find 'Sales Department'
        dept_to_remove = db.query(models.Department).filter(models.Department.Name == "Sales Department").first()
        
        if dept_to_remove:
            print(f"Found department to remove: {dept_to_remove.Name} (ID: {dept_to_remove.Id})")
            
            # Check if any users are assigned to this department
            users_count = db.query(models.User).filter(models.User.DepartmentId == dept_to_remove.Id).count()
            
            if users_count > 0:
                print(f"Warning: There are {users_count} users assigned to this department.")
                # Migrate users to 'Sales' department if it exists
                sales_dept = db.query(models.Department).filter(models.Department.Name == "Sales").first()
                if sales_dept:
                    print(f"Migrating users to 'Sales' department (ID: {sales_dept.Id})...")
                    db.query(models.User).filter(models.User.DepartmentId == dept_to_remove.Id).update(
                        {models.User.DepartmentId: sales_dept.Id}
                    )
                    db.commit()
                    print("Users migrated.")
                else:
                    print("Error: 'Sales' department not found to migrate users to. Aborting delete.")
                    return

            db.delete(dept_to_remove)
            db.commit()
            print("Successfully deleted 'Sales Department'.")
        else:
            print("'Sales Department' not found.")

    except Exception as e:
        print(f"Error removing department: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remove_duplicate_sales()
