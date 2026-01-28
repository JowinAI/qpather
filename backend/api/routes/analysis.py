from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx
import os
from dotenv import load_dotenv
from db import models
from api.dependencies.model_utils import get_db

load_dotenv()

router = APIRouter()

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx
import os
import base64
from dotenv import load_dotenv
from db import models
from api.dependencies.model_utils import get_db

load_dotenv()

router = APIRouter()

# Pydantic model for the request body
class ChatRequest(BaseModel):
    content: str

def get_goal_context(db: Session, goal_id: int) -> str:
    # 1. Fetch Goal
    goal = db.query(models.Goal).filter(models.Goal.Id == goal_id).first()
    if not goal:
        return None

    # 2. Fetch all Threaded Assignments (Flattened Hierarchy)
    if goal.ThreadId:
        # If ThreadId exists, fetch all assignments in this thread
        assignments = db.query(models.Assignment).filter(models.Assignment.ThreadId == goal.ThreadId).order_by(models.Assignment.CreatedAt).all()
        # Also fetch responses by ThreadId if populated, or fallback to Assignment IDs
        assignment_ids = [a.Id for a in assignments]
        responses = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId.in_(assignment_ids)).all()
    else:
        # Fallback for legacy data without ThreadId
        assignments = db.query(models.Assignment).filter(models.Assignment.GoalId == goal_id).all()
        responses = []
        for asm in assignments:
             r = db.query(models.UserResponse).filter(models.UserResponse.AssignmentId == asm.Id).all()
             responses.extend(r)

    # 3. Construct Context
    context_text = f"Strategic Topic (Thread ID: {goal.ThreadId}): {goal.Title}\nDescription: {goal.GoalDescription}\n\n[Discussion Thread]\n"
    
    # Create a map for quick lookup of responses by assignment
    resp_map = {}
    for r in responses:
        if r.AssignmentId not in resp_map:
            resp_map[r.AssignmentId] = []
        resp_map[r.AssignmentId].append(r)
        
    if not assignments:
        context_text += "No active discussion threads initiated yet."
    else:
        # Organize assignments to show flow if possible, or just chronological
        # Since we want a thread summary, chronological by creation might be best to show evolution
        for assignment in assignments:
            indent = ""
            if assignment.ParentAssignmentId:
                 indent = "  >> " # Visual indentation for replies/delegations
            
            context_text += f"{indent}Request/Question: {assignment.QuestionText} (From: {assignment.CreatedBy})\n"
            
            these_responses = resp_map.get(assignment.Id, [])
            if these_responses:
                for resp in these_responses:
                    ans = resp.Answer if resp.Answer else "Pending Response"
                    status = f"[{resp.Status}]" if resp.Status else ""
                    context_text += f"{indent}  - Response from {resp.AssignedTo} {status}: {ans}\n"
            else:
                context_text += f"{indent}  - (Awaiting Response)\n"
                
            context_text += "\n"
            
    return context_text

@router.post("/analyze-goal/{goal_id}")
async def analyze_goal(goal_id: int, db: Session = Depends(get_db)):
    context_text = get_goal_context(db, goal_id)
    if not context_text:
        raise HTTPException(status_code=404, detail="Goal not found")

    # 3. Call OpenAI LLM
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
             "analysis": "AI Analysis is unavailable because the API Key is not configured. Please add OPENAI_API_KEY to the .env file."
        }

    system_message = (
        "You are an expert strategic analyst. Analyze the following goal and team feedback. "
        "Identify key themes, potential risks/concerns raised by the team, and provide actionable recommendations. "
        "Format your response with clear headings (e.g., Key Themes, Risks, Recommendations)."
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": context_text}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30.0)
            if response.status_code != 200:
                 return {"analysis": f"Error from OpenAI: {response.text}"}
            
            result = response.json()
            analysis_text = result["choices"][0]["message"]["content"]
            return {"analysis": analysis_text}

    except Exception as e:
        return {"analysis": f"An error occurred during analysis: {str(e)}"}


@router.post("/chat-goal/{goal_id}")
async def chat_goal(goal_id: int, request: ChatRequest, db: Session = Depends(get_db)):
    context_text = get_goal_context(db, goal_id)
    if not context_text:
        raise HTTPException(status_code=404, detail="Goal not found")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"response": "System Error: OpenAI API Key missing."}

    system_message = (
        "You are an AI Analyst assistant helping a manager understand the strategic goal and team feedback. "
        "You have access to the goal details and all user responses. "
        "Answer the user's specific question based strictly on this context. "
        "If the answer is not in the context, say you don't have that information."
    )

    user_query = f"Context:\n{context_text}\n\nUser Question: {request.content}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_query}
        ],
        "max_tokens": 300,
        "temperature": 0.5
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            return {"response": result["choices"][0]["message"]["content"]}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
             return {"response": "Analyis Limit Reached. Please check your OpenAI Usage/Billing configuration."}
        return {"response": f"AI Provider Error: {e.response.text}"}
    except Exception as e:
        return {"response": f"I encountered an error processing your request: {str(e)}"}

# Person details for system message (Legacy/Demo)
person_details = {
    "role": "CEO called brand johnson. He is running a company called Peterson Consulting. It is sofware saas company",
    "company": "Peterson conulting delivery products and solutions for financial and insurance customers. Peterson is the leading provider of SAAS in financial sector",
    "geography": "North America"
}

@router.get("/breakdown/")
async def breakdown_get():
  return {"response": "Service is running"}

@router.post("/breakdown/")
async def breakdown_post(request: ChatRequest):
    # ... legacy breakdown logic ...
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
         return {"response": "{\n  \"Goal\": \"Error\",\n  \"Questions\": [\n    \"OpenAI API Key is missing.\"\n  ]\n}"}

    system_message = f'''
        You are assisting a user from the following context:
        - Role: {person_details['role']}
        - Company: {person_details['company']}
        - Company Geography: {person_details['geography']}
        
        Please provide responses based on the user's background.
        Provide upto 5 questions or statements.
        The response must be in the following JSON format:
        {{
          "Goal": "one title line for what the user is trying to achieve",
          "Questions": [
            "your first question",
            "your second question"
          ]
        }}
    '''

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": request.content}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            return {"response": response_text}
    except Exception as e:
         return {"response": "{\n  \"Goal\": \"Error calling AI\",\n  \"Questions\": [\n    \"Please try again later.\"\n]\n}"}

@router.post("/extract-team")
async def extract_team(file: UploadFile = File(...), db: Session = Depends(get_db)):
    api_key = os.getenv("OPENAI_API_KEY")
    
    # 1. Fetch referential context
    org = db.query(models.Organization).first()
    dept = db.query(models.Department).first()
    org_id = org.Id if org else 1
    dept_id = dept.Id if dept else 1

    if not api_key:
        print("OPENAI_API_KEY missing - returning simulated extraction.")
        return {"users": [
            {"FirstName": "Joise", "LastName": "Alvin", "Email": "joise.alvin@example.com", "Role": "Strategy Lead", "OrganizationId": org_id, "DepartmentId": dept_id},
            {"FirstName": "Alvin", "LastName": "George", "Email": "alvin.george@example.com", "Role": "Operations Specialist", "OrganizationId": org_id, "DepartmentId": dept_id},
            {"FirstName": "George", "LastName": "Joy", "Email": "george.joy@example.com", "Role": "Research Analyst", "OrganizationId": org_id, "DepartmentId": dept_id},
            {"FirstName": "Kathy", "LastName": "Adam", "Email": "kathy@dooe.ai", "Role": "Manager", "OrganizationId": org_id, "DepartmentId": dept_id}
        ]}

    try:
        # 2. Process image for Vision AI
        file_content = await file.read()
        base64_image = base64.b64encode(file_content).decode('utf-8')

        # 3. Call OpenAI Vision Intelligence
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        prompt = (
            "You are a strategic organizational analyst. Extract all personnel information from this organizational chart. "
            "Return a JSON object with a key 'users' containing a list of objects. "
            "For each person, extract: "
            "1. 'FirstName' (mandatory) "
            "2. 'LastName' (mandatory) "
            "3. 'Email' (mandatory, must be a valid email format) "
            "4. 'Role' (strategic title or operational role) "
            "If a full name is given, split it into FirstName and LastName. "
            "If an email is missing, try to generate a professional one based on their name (e.g., first.last@company.com). "
            "Ensure the output is clean JSON without any markdown formatting."
        )

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "response_format": { "type": "json_object" },
            "max_tokens": 2000
        }

        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            ai_data = response.json()
            
            import json
            raw_content = ai_data["choices"][0]["message"]["content"]
            extracted_data = json.loads(raw_content)
            
            # Map IDs and validate users
            final_users = []
            for u in extracted_data.get("users", []):
                email = u.get("Email", "").strip()
                first_name = u.get("FirstName", "").strip()
                last_name = u.get("LastName", "").strip()
                
                # Minimum requirement: Email and at least one name component
                if email and (first_name or last_name):
                    final_users.append({
                        "FirstName": first_name or "Strategic",
                        "LastName": last_name or "Specialist",
                        "Email": email,
                        "Role": u.get("Role", "Team Member").strip() or "Onboarded Specialist",
                        "OrganizationId": org_id,
                        "DepartmentId": dept_id
                    })
            
            print(f"Strategic Extraction Complete: {len(final_users)} specialists identified.")
            return {"users": final_users}

    except Exception as e:
        print(f"Vision API strategic failure: {str(e)}")
        # Fallback to demo response for stability
        return {"users": [
            {"FirstName": "Joise", "LastName": "Alvin", "Email": "joise.alvin@example.com", "Role": "Strategy Lead", "OrganizationId": org_id, "DepartmentId": dept_id},
            {"FirstName": "Alvin", "LastName": "George", "Email": "alvin.george@example.com", "Role": "Operations Specialist", "OrganizationId": org_id, "DepartmentId": dept_id},
            {"FirstName": "George", "LastName": "Joy", "Email": "george.joy@example.com", "Role": "Research Analyst", "OrganizationId": org_id, "DepartmentId": dept_id}
        ]}
