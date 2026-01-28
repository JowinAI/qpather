from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Use the one seen in logs if not in .env
    DATABASE_URL = "mssql+pyodbc://db_aa36ea_qpather_admin:Nijesh2024@SQL5112.site4now.net:1433/db_aa36ea_qpather?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"

engine = create_engine(DATABASE_URL)

def migrate():
    columns_to_add = [
        ("PasswordHash", "VARCHAR(255)"),
        ("Bio", "TEXT"),
        ("DecisionStyle", "VARCHAR(100)"),
        ("Status", "VARCHAR(50)"),
        ("CreatedBy", "VARCHAR(255)"),
        ("UpdatedBy", "VARCHAR(255)")
    ]
    
    with engine.connect() as conn:
        print("Starting manual migration...")
        for col_name, col_type in columns_to_add:
            try:
                # SQL Server syntax for adding column if not exists
                query = text(f"ALTER TABLE [user] ADD {col_name} {col_type}")
                conn.execute(query)
                conn.commit()
                print(f"✅ Added column: {col_name}")
            except Exception as e:
                if "already exists" in str(e).lower() or "Duplicate column name" in str(e) or "2705" in str(e):
                    print(f"ℹ️ Column {col_name} already exists.")
                else:
                    print(f"❌ Error adding {col_name}: {e}")

if __name__ == "__main__":
    migrate()
