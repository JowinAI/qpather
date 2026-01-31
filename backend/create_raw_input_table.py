from db.database import engine, SessionLocal
from db import models
from sqlalchemy import text

def create_table():
    print("Creating RawContextInput table...")
    try:
        models.Base.metadata.create_all(bind=engine)
        print("Table created successfully (if it didn't exist).")
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_table()
