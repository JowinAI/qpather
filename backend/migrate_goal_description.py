import sys
import os
from sqlalchemy import text

# Add the script's directory to sys.path to ensure imports work regardless of CWD
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from db.database import SessionLocal

def alter_table():
    db = SessionLocal()
    try:
        print("Migrating 'goal' table schema...")
        
        # Alter the column to NVARCHAR(MAX) to support unlimited text
        sql = "ALTER TABLE goal ALTER COLUMN GoalDescription NVARCHAR(MAX)"
        
        db.execute(text(sql))
        db.commit()
        print("Successfully altered GoalDescription column to NVARCHAR(MAX)")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    alter_table()
