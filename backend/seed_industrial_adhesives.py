import sys
import os
from datetime import datetime, timedelta
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from db.database import SessionLocal, engine
    from db.models import User, Goal, Assignment, UserResponse, GoalDashboardInsight, Organization
except ImportError:
    # Fallback if run from different dir
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from db.database import SessionLocal, engine
    from db.models import User, Goal, Assignment, UserResponse, GoalDashboardInsight, Organization

db = SessionLocal()

def seed():
    print("Seeding Industrial Adhesives Scenario...")
    
    # 1. Ensure Organization
    org = db.query(Organization).first()
    if not org:
        org = Organization(Name="Industrial Adhesives Inc", ClientId=1)
        db.add(org)
        db.commit()
        print(f"Created Org: {org.Name}")
    else:
        print(f"Using Org: {org.Name}")

    # 2. Create Users
    users_data = [
        {"firstName": "George", "lastName": "Thomas", "email": "george.thomas@example.com", "role": "Sr. Vice President", "status": "ACTIVE"},
        {"firstName": "Michael", "lastName": "Reynolds", "email": "michael.reynolds@example.com", "role": "VP Finance", "status": "ACTIVE"},
        {"firstName": "Jason", "lastName": "Patel", "email": "jason.patel@example.com", "role": "Sales Lead", "status": "ACTIVE"},
        {"firstName": "Kevin", "lastName": "ONeil", "email": "kevin.oneil@example.com", "role": "FP&A Manager", "status": "ACTIVE"},
        {"firstName": "Sarah", "lastName": "Kim", "email": "sarah.kim@example.com", "role": "Global Segment Director", "status": "ACTIVE"},
        {"firstName": "David", "lastName": "Alvarez", "email": "david.alvarez@example.com", "role": "Global Segment Director", "status": "ACTIVE"},
        {"firstName": "Laura", "lastName": "Bennett", "email": "laura.bennett@example.com", "role": "Global Segment Director", "status": "ACTIVE"},
        {"firstName": "Anil", "lastName": "Verma", "email": "anil.verma@example.com", "role": "VP Product", "status": "ACTIVE"},
        {"firstName": "Rachel", "lastName": "Moore", "email": "rachel.moore@example.com", "role": "Pricing Lead", "status": "ACTIVE"},
    ]

    user_map = {}
    for u in users_data:
        existing = db.query(User).filter(User.Email == u['email']).first()
        if not existing:
            existing = User(OrganizationId=org.Id, FirstName=u['firstName'], LastName=u['lastName'], Email=u['email'], Role=u['role'], Status=u['status'])
            db.add(existing)
            db.commit()
            print(f"Created User: {u['email']}")
        user_map[u['firstName']] = existing

    # 3. Create Goal
    goal_title = "Industrial Adhesives – Growth, Margin & Execution Health"
    goal = db.query(Goal).filter(Goal.Title == goal_title).first()
    if not goal:
        goal = Goal(
            Title=goal_title,
            OrganizationId=org.Id,
            InitiatedBy=user_map["George"].Email,
            GoalDescription="Are we on track to meet FY growth and margin targets across the Industrial Adhesives business in the Americas?",
            DueDate=datetime.now() + timedelta(days=90),
            CreatedBy=user_map["George"].Email  # Fix: Must set CreatedBy
        )
        db.add(goal)
        db.commit()
        print(f"Created Goal: {goal.Title}")
    else:
        # Check if CreatedBy is null and fix it
        if not goal.CreatedBy:
            goal.CreatedBy = user_map["George"].Email
            db.commit()
            print(f"Fixed missing CreatedBy for Goal: {goal.Title}")
        print(f"Using Goal: {goal.Title} (ID: {goal.Id})")

    # 4. Create Assignments (Level 1)
    questions = [
        {"q": "Are we tracking to revenue and margin targets...", "user": "Michael"},
        {"q": "Are we closing enough new projects...", "user": "Jason", "ans": "Pipeline volume is healthy, but conversion is slowing due to pricing pushback and delayed customer approvals."},
        {"q": "Is the current order book at levels consistent...", "user": "Kevin", "ans": "Order book is slightly below plan for this point in the fiscal year, particularly in Solar."},
        {"q": "What is the demand outlook and top execution risks...", "user": "Sarah", "ans": "Demand strong but risks from qualification delays."},
        {"q": "Are pricing, policy, or supply chain issues impacting Solar...", "user": "David", "ans": "Competitors are offering aggressive discounts, impacting win rates."},
        {"q": "Are there any qualification delays...", "user": "Laura"},
        {"q": "Is the product roadmap aligned with growth segments...", "user": "Anil", "ans": "Qualification for a new adhesive formulation is delayed by approximately four weeks."},
        {"q": "Are we experiencing pricing pressure...", "user": "Rachel"},
    ]

    for idx, q_data in enumerate(questions):
        u = user_map[q_data['user']]
        assign = db.query(Assignment).filter(Assignment.GoalId == goal.Id, Assignment.QuestionText.like(f"{q_data['q'][:20]}%")).first()
        if not assign:
            assign = Assignment(GoalId=goal.Id, QuestionText=q_data['q'], Order=idx+1, CreatedBy=user_map["George"].Email)
            db.add(assign)
            db.commit()
            print(f"Created Assignment: {q_data['q'][:20]}...")
        else:
            if not assign.CreatedBy:
                assign.CreatedBy = user_map["George"].Email
                db.commit()
        
        # Create Response/Assignment link
        resp = db.query(UserResponse).filter(UserResponse.AssignmentId == assign.Id).first()
        if not resp:
            answer_text = q_data.get('ans')
            resp = UserResponse(AssignmentId=assign.Id, AssignedTo=u.Email, Answer=answer_text, Status="Completed" if answer_text else "Assigned", CreatedBy=u.Email)
            db.add(resp)
            db.commit()
        else:
            if not resp.CreatedBy:
                resp.CreatedBy = u.Email
                db.commit()

    # 6. Create GoalDashboardInsight
    import hashlib
    
    # Frontend Default Settings (Must match src/pages/dashboard/goal/[id].tsx systemDefault)
    default_settings = {
      "lensName": "Executive Forward Risk (Default)",
      "focusSignals": ["Revenue & Margin", "Sales Pipeline"],
      "focusQuestions": ["What are the top 3 risks to delivery?"],
      "sections": {
        "executiveSummary": True,
        "signalHealth": True,
        "topRisks": True,
        "conflicts": True,
        "patterns": True,
        "actions": True,
        "dataGaps": True,
        "evidence": True,
        "focusQna": True
      },
      "display": {
        "timeHorizon": "Quarterly",
        "verbosity": "Executive Summary",
        "maxRisks": 3,
        "maxActions": 3
      }
    }

    def generate_lens_signature(settings_dict):
        s_json = json.dumps(settings_dict, sort_keys=True)
        return hashlib.md5(s_json.encode()).hexdigest()

    lens_sig = generate_lens_signature(default_settings)
    print(f"Generated Lens Signature: {lens_sig}")

    insight_data = {
        "overall_status": "At Risk",
        "aggregate_confidence": 0.68,
        "as_of_date": datetime.now().strftime("%Y-%m-%d"),
        "executive_summary": "Demand exists, but execution and conversion are lagging. Order book not yet at levels required to confidently hit growth targets. Margin pressure persists across segments.",
        "signal_health": [
            {"signal_name": "Sales Pipeline", "signal_type": "Execute", "status": "Yellow", "key_points": ["Pipeline size adequate", "Conversion rates below plan", "Pricing pressure impacting close rates"]},
            {"signal_name": "Order Book", "signal_type": "Health", "status": "Red", "key_points": ["Trending slightly below growth targets", "Solar segment most impacted"]},
            {"signal_name": "Financials", "signal_type": "Finance", "status": "Yellow", "key_points": ["Revenue slightly below plan", "Margin erosion risk confirmed"]}
        ],
        "top_risks": [
            {"risk": "Sales pipeline conversion below plan", "severity": "High", "confidence": 0.65, "owner_suggestions": ["Jason Patel"], "drivers": ["Pricing", "Delays"]},
            {"risk": "Solar pricing pressure reducing wins", "severity": "High", "confidence": 0.60, "owner_suggestions": ["Rachel Moore"], "drivers": ["Competition"]},
            {"risk": "Power qualification delays", "severity": "Medium", "confidence": 0.70, "owner_suggestions": ["Anil Verma"], "drivers": ["R&D"]}
        ],
        "recommended_actions": [
            {"action": "Improve pipeline conversion strategy", "owner": "Jason Patel", "due_horizon": "Immediate", "expected_impact": "High"},
            {"action": "Review order book coverage vs. plan", "owner": "Kevin O'Neil", "due_horizon": "1 Week", "expected_impact": "High"},
            {"action": "Accelerate Power qualification", "owner": "Anil Verma", "due_horizon": "2 Weeks", "expected_impact": "Medium"},
             {"action": "Reassess Solar pricing strategy", "owner": "Rachel Moore", "due_horizon": "1 Week", "expected_impact": "High"}
        ],
        "conflicts": [
            {"topic": "Execution vs Constraints", "conflict_description": "Sales reports strong pipeline, but Finance and Operations report execution and supply constraints."}
        ]
    }

    exist_insight = db.query(GoalDashboardInsight).filter(GoalDashboardInsight.GoalId == goal.Id).first()
    if exist_insight:
        exist_insight.InsightJson = json.dumps(insight_data)
        exist_insight.LensSignature = lens_sig # Update signature
        print("Updated Insight with Signature")
    else:
        exist_insight = GoalDashboardInsight(
            GoalId=goal.Id, 
            InsightJson=json.dumps(insight_data), 
            ModelUsed="gpt-4", 
            PromptVersion="v1",
            LensSignature=lens_sig
        )
        db.add(exist_insight)
        print("Created Insight with Signature")

    db.commit()
    print(f"SEED COMPLETE. Goal ID: {goal.Id}")

if __name__ == "__main__":
    seed()
