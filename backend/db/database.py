from sqlalchemy.orm import declarative_base, sessionmaker, with_loader_criteria, Session
from sqlalchemy import create_engine, event
from sqlalchemy.event import listens_for
import struct
import os
import json
import constants
from db import models
from azure import identity


SQL_COPT_SS_ACCESS_TOKEN = 1256  # Connection option for access tokens, as defined in msodbcsql.h
TOKEN_URL = "https://database.windows.net/"  # The token URL for any Azure SQL database

#connection_string = "mssql+pyodbc://sqladmin:Molutty240$@qpather-qa-sql.database.windows.net:1433/qpather-qa?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
connection_string = "mssql+pyodbc://db_aa36ea_qpather_admin:Molutty240$@SQL5112.site4now.net:1433/db_aa36ea_qpather?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
print(f"Connection string: {connection_string}")
engine = create_engine(connection_string)  # , echo=True)  # echo=True for debugging sqlalchemy queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# @event.listens_for(Session, "do_orm_execute")
# def _do_orm_execute(orm_execute_state):

#     if (
#         orm_execute_state.is_select
#         and not orm_execute_state.is_column_load
#         and not orm_execute_state.is_relationship_load
#         ):
#         orm_execute_state.statement = orm_execute_state.statement.options(
#             with_loader_criteria(
#                 models.Project, models.Project.IsDelete == False)
#         )

try:
    session = SessionLocal()
except Exception as e:
    print(f"Error creating session: {str(e)}")


# Create a base class for declarative models
Base = declarative_base()
