
from sqlalchemy import create_engine, text

# Database configuration
DATABASE_URL = "mssql+pyodbc://db_aa36ea_qpather_admin:Nijesh2024@SQL5112.site4now.net/db_aa36ea_qpather?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes"

engine = create_engine(DATABASE_URL)

def check_goal_118():
    with engine.connect() as conn:
        print("--- Checking Goal 118 Assignments ---")
        
        # Get all assignments for Goal 118
        assignments = conn.execute(text("SELECT Id, QuestionText, ParentAssignmentId, CreatedBy, [Order], ThreadId FROM assignment WHERE GoalId = 118 ORDER BY [Order]")).fetchall()
        
        # Get user responses
        responses = conn.execute(text("SELECT AssignmentId, AssignedTo, Answer, Status FROM userresponse WHERE AssignmentId IN (SELECT Id FROM assignment WHERE GoalId = 118)")).fetchall()
        response_map = {}
        for r in responses:
            if r.AssignmentId not in response_map:
                response_map[r.AssignmentId] = []
            response_map[r.AssignmentId].append(f"{r.AssignedTo} ({r.Status})")

        print(f"Total Assignments: {len(assignments)}")
        for a in assignments:
            resps = response_map.get(a.Id, ["No responses"])
            print(f"ID: {a.Id}, Parent: {a.ParentAssignmentId}, Creator: {a.CreatedBy}, Order: {a.Order}, ThreadId: {a.ThreadId}, Text: {a.QuestionText[:50]}... -> Responses: {', '.join(resps)}")

        print("\n--- Checking for Orphaned Children ---")
        parent_ids = [a.Id for a in assignments]
        print("\n--- Checking for Assignments by ThreadId ---")
        thread_id = "f522e4ec-9f47-44a3-93c1-a6caf7d035d0"
        thread_orphans = conn.execute(text(f"SELECT Id, GoalId, ParentAssignmentId, QuestionText FROM assignment WHERE ThreadId = '{thread_id}' AND (GoalId != 118 OR GoalId IS NULL)")).fetchall()
        print(f"ThreadId Orphans Count: {len(thread_orphans)}")
        for o in thread_orphans:
             print(f"  - Hidden Child! ID: {o.Id}, GoalId: {o.GoalId}, Parent: {o.ParentAssignmentId}, Text: {o.QuestionText}")

if __name__ == "__main__":
    check_goal_118()
