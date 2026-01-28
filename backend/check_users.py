from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import models
import logging

# Setup logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Connection string from db/database.py
connection_string = "mssql+pyodbc://db_aa36ea_qpather_admin:Nijesh2024@SQL5112.site4now.net:1433/db_aa36ea_qpather?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"

engine = create_engine(connection_string)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

emails = ["joise.alvin@gmail.com", "alvingeorge@gmail.com"]

print("--- User Check ---")
for email in emails:
    user = session.query(models.User).filter(models.User.Email == email).first()
    if user:
        print(f"User Found: {user.Email}, Status: {user.Status}, ID: {user.Id}, OrgId: {user.OrganizationId}")
    else:
        print(f"User Not Found: {email}")
print("--- End Check ---")
