from db.database import engine
from db.models import Base

def create_tables():
    print("Creating all tables from models...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()
