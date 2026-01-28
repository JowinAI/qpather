import os
import sqlalchemy
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dooe")
engine = create_engine(DATABASE_URL)

def search_email(email):
    tables = [
        "user",
        "userresponse",
        "auditlog",
        "usersettings",
        "organization",
        "client"
    ]
    
    with engine.connect() as connection:
        for table in tables:
            print(f"Searching in table: {table}")
            try:
                if table == "user":
                    query = text(f"SELECT * FROM \"{table}\" WHERE \"Email\" ILIKE :email")
                elif table == "userresponse":
                    query = text(f"SELECT * FROM \"{table}\" WHERE \"AssignedTo\" ILIKE :email")
                elif table == "auditlog":
                    query = text(f"SELECT * FROM \"{table}\" WHERE \"UserId\" ILIKE :email")
                elif table == "usersettings":
                    # usersettings joins with user
                    query = text(f"SELECT \"usersettings\".* FROM \"usersettings\" JOIN \"user\" ON \"usersettings\".\"UserId\" = \"user\".\"Id\" WHERE \"user\".\"Email\" ILIKE :email")
                elif table == "organization":
                    query = text(f"SELECT * FROM \"{table}\" WHERE \"ContactEmail\" ILIKE :email")
                elif table == "client":
                    query = text(f"SELECT * FROM \"{table}\" WHERE \"ContactEmail\" ILIKE :email")
                else:
                    continue
                
                result = connection.execute(query, {"email": email}).fetchall()
                if result:
                    print(f"Found {len(result)} records in {table}:")
                    for row in result:
                        print(dict(row._mapping))
                else:
                    print(f"No records found in {table}.")
            except Exception as e:
                print(f"Error querying {table}: {e}")
            print("-" * 20)

if __name__ == "__main__":
    search_email("joisetest@gmail.com")
