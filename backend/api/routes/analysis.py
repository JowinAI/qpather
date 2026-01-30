from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx
import os
import json
import hashlib
import base64
from datetime import datetime
from dotenv import load_dotenv
from db import models, schemas
from api.dependencies.model_utils import get_db
import jwt
from jwt import PyJWTError
from typing import Optional

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-tokens-change-this-in-prod")
ALGORITHM = "HS256"

# Helper to get user from token (similar to dashboard_settings)
async def get_current_user_optional(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        return None
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
             return None
    except PyJWTError:
        return None
    
    user = db.query(models.User).filter(models.User.Email == email).first()
    return user

def get_goal_context(db: Session, goal_id: int) -> str:
    goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()
    if not goal:
        return ""
    
    context = f"Strategic Goal: {goal.Title}\nDescription: {goal.GoalDescription or ''}\n\nKey Discussions:\n"
    
    assignments = db.query(models.Assignment).filter(models.Assignment.GoalId == goal_id).all()
    for asm in assignments:
        context += f"Inquiry: {asm.QuestionText}\n"
        responses = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == asm.Id).all()
        for r in responses:
            context += f" - Response ({r.AssignedTo}): {r.Answer or 'Pending'}\n"
        context += "\n"
        
    return context

def generate_lens_signature(settings: schemas.DashboardSettingsPayload) -> str:
    # Generate a unique hash for the settings configuration
    # Only relevant fields: lensName, focusSignals, focusQuestions (content), sections (which enabled)
    # Display prefs might update UI but dont necessarily change the underlying DATA analysis? 
    # Actually, verbosity changes summary length. So yes, include all.
    s_dict = settings.model_dump()
    s_json = json.dumps(s_dict, sort_keys=True)
    return hashlib.md5(s_json.encode()).hexdigest()

def get_hierarchy_data(db: Session, goal_id: int) -> schemas.HierarchyData:
    nodes = []
    
    # Root Goal
    goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()
    if not goal:
         return schemas.HierarchyData(nodes=[])
    
    # Assignments (Q)
    assignments = db.query(models.Assignment).filter(models.Assignment.GoalId == goal_id).all()
    
    for asm in assignments:
        # User Responses (R)
        responses = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == asm.Id).all()
        
        response_list = []
        for r in responses:
            # Assigner/Responder details
            # In a real app we'd fetch User objects. Here using raw string or mock
            responder_name = r.AssignedTo # Usually email
            
            response_list.append({
                "response_id": f"R{r.Id}",
                "from": {"name": responder_name, "email": responder_name, "role": "Contributor"},
                "text": r.Answer or "No response",
                "confidence": 0.8 # Placeholder or derived
            })
            
        nodes.append(schemas.HierarchyNode(
            node_id=f"Q{asm.Id}",
            level=1,
            parent_id=f"G{goal.Id}",
            signal={"name": "General", "type": "execution"}, # Logic to map Question -> Signal?
            assigned_to={"name": "Assignee", "email": "assignee@example.com", "role": "Owner"},
            question=asm.QuestionText,
            responses=response_list
        ))
        
    return schemas.HierarchyData(nodes=nodes)

@router.get("/goals/{goal_id}/dashboard/insight")
async def get_dashboard_insight(
    goal_id: int, 
    lensSignature: str, 
    db: Session = Depends(get_db)
):
    insight = db.query(models.GoalDashboardInsight).filter(
        models.GoalDashboardInsight.GoalId == goal_id,
        models.GoalDashboardInsight.LensSignature == lensSignature
    ).order_by(models.GoalDashboardInsight.CreatedAt.desc()).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
        
    return json.loads(insight.InsightJson)

@router.post("/goals/{goal_id}/dashboard/insight/retrieve")
async def retrieve_dashboard_insight(
    goal_id: int, 
    settings: schemas.DashboardSettingsPayload, 
    db: Session = Depends(get_db)
):
    lens_sig = generate_lens_signature(settings)
    insight = db.query(models.GoalDashboardInsight).filter(
        models.GoalDashboardInsight.GoalId == goal_id,
        models.GoalDashboardInsight.LensSignature == lens_sig
    ).order_by(models.GoalDashboardInsight.CreatedAt.desc()).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
        
    return json.loads(insight.InsightJson)

@router.post("/goals/{goal_id}/dashboard/analyze")
async def analyze_dashboard(
    goal_id: int, 
    settings: schemas.DashboardSettingsPayload, 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    # 1. Check for existing content? No, POST implies Re-Analyze (Refresh).
    # Frontend handles "Check existing" via GET /insight.
    
    # 2. Build Hierarchy Context
    goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()
    if not goal:
         raise HTTPException(status_code=404, detail="Goal not found")
    
    hierarchy = get_hierarchy_data(db, goal_id)
    
    # 3. Viewer Context
    viewer_context = {
        "name": current_user.FirstName if current_user else "Exec",
        "email": current_user.Email if current_user else "exec@company.com",
        "role": current_user.Role if current_user else "Executive"
    }
    
    # 4. Construct Payload for OpenAI
    # We construct the "AnalysisRequest" JSON structure described in prompt
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
         raise HTTPException(status_code=500, detail="OPENAI_API_KEY is missing in environment variables. Real analysis requires a valid API key.")

    system_message = (
        "You are DOOE AI, an executive decision-intelligence engine. "
        "Produce an executive dashboard analysis. "
        "Output MUST be valid JSON with the following keys: "
        "executive_summary (string), overall_status (Green/Yellow/Red), "
        "aggregate_confidence (0.0-1.0), as_of_date (YYYY-MM-DD), "
        "signal_health (array of {signal_name, status, signal_type, key_points}), "
        "top_risks (array of {risk, severity, drivers, owner_suggestions, confidence}), "
        "recommended_actions (array of {action, owner, due_horizon, expected_impact}), "
        "detected_patterns (array of {pattern_name, description}), "
        "conflicts (array of {topic, conflict_description}), "
        "focus_qna (array of {question, answer_bullets}), "
        "data_gaps (string array)."
    )

    # Convert Pydantic models to dicts
    request_payload = {
        "viewer_context": viewer_context,
        "goal_context": {
            "goal_id": str(goal_id),
            "goal_title": goal.Title,
            "goal_text": goal.GoalDescription or "",
            "as_of_date": datetime.now().strftime("%Y-%m-%d")
        },
        "dashboard_request": settings.model_dump(),
        "hierarchy": hierarchy.model_dump(),
        "rules": {
            "signal_weighting": { "leading": 1.4, "execution": 1.3, "constraint": 1.2, "market": 1.1, "lagging": 1.0 },
            "status_thresholds": { "green": 0.75, "yellow": 0.60, "red": 0.00 }
        }
    }
    
    prompt_str = json.dumps(request_payload, default=str)

    payload = {
        "model": "gpt-3.5-turbo-1106",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_str}
        ],
        "response_format": { "type": "json_object" },
        "max_tokens": 2000,
        "temperature": 0.4
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 5. Persist Result
            lens_sig = generate_lens_signature(settings)
            
            insight_obj = models.GoalDashboardInsight(
                GoalId=goal_id,
                UserId=current_user.Id if current_user else None,
                LensSignature=lens_sig,
                InsightJson=content,
                ModelUsed="gpt-3.5-turbo-1106",
                CreatedAt=datetime.now()
            )
            db.add(insight_obj)
            db.commit()
            
            return json.loads(content)

    except Exception as e:
        print(f"Analysis Failed: {e}")
        return {
            "executive_summary": "Analysis failed due to error.",
            "error": str(e)
        }

@router.post("/goals/{goal_id}/dashboard/chat")
async def chat_dashboard(
    goal_id: int, 
    request: schemas.ChatRequest, 
    db: Session = Depends(get_db)
):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
         return {"answer": "System Error: OpenAI API Key missing.", "bullets": []}

    # Auto-fetch hierarchy if not provided by frontend
    if not request.hierarchy or not request.hierarchy.nodes:
         request.hierarchy = get_hierarchy_data(db, goal_id)

    system_message = (
        "You are DOOE AI, the executive assistant for this goal. "
        "Answer the user question using ONLY the provided hierarchy data and insight snapshot. "
        "Be concise, cite supporting node_ids for key claims. "
        "Return JSON: { \"answer\": \"...\", \"bullets\": [...], \"supporting_nodes\": [...], \"confidence\": ... }"
    )
    
    # We use the request from frontend which includes insight_snapshot
    prompt_str = request.model_dump_json()

    payload = {
        "model": "gpt-3.5-turbo-1106",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_str}
        ],
        "response_format": { "type": "json_object" },
        "max_tokens": 500,
        "temperature": 0.5
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=45.0)
            response.raise_for_status()
            result = response.json()
            return json.loads(result["choices"][0]["message"]["content"])
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "bullets": []}

# ... Keep Legacy Endpoints if needed or minimal mocks ...
@router.post("/extract-team")
async def extract_team(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return {"users": []} # Simplified stub as focus is Dashboard

@router.post("/enhance")
async def enhance_text(request: schemas.EnhanceRequest): # Using schema from schemas.py expected?
    return {"text": request.text}

@router.post("/breakdown/")
async def analyze_goal_breakdown(request: schemas.BreakdownRequest):
    import os
    import json
    import httpx
    
    api_key = os.getenv("OPENAI_API_KEY")
    # If no key, return mock data to allow flow to proceed
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is missing. Real analysis required.")

    system_message = (
        "You are a strategic assistant. Analyze the user's input. "
        "Return a JSON object with two keys: 'Goal' (a refined, high-level summary of the objective) "
        "and 'Questions' (a list of 3-5 strategic questions to break down this goal). "
        "Output JSON only."
    )

    payload = {
        "model": "gpt-3.5-turbo-1106",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": request.content}
        ],
        "response_format": { "type": "json_object" },
        "max_tokens": 1000
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return {"response": content}
        except Exception as e:
            print(f"Breakdown Error: {e}")
            raise HTTPException(status_code=500, detail=f"AI Breakdown Failed: {str(e)}")
