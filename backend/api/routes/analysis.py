from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os   

router = APIRouter()

# Replace this with your actual API key or load from environment variables
API_KEY = os.getenv("OPENAI_API_KEY", "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")

# Pydantic model for the request body
class ChatRequest(BaseModel):
    content: str

# Person details for system message
person_details = {
    "role": "Responsible for the Henkel Adhesive Industrial's SBU America’s and Global Telecom, Power and Solar Segments. Highly motivated and experienced business leader with expert proficiency in providing unsurpassed leadership and revenue growth in a dynamic, fast-paced, competitive business environment, consistently rated as a top performer within the global organization. Offers expertise in P&L management, marketing leadership, engineering, operations, and technology management.",
    "company": "Henkel operates worldwide with leading innovations, brands, and technologies in two business areas: Adhesive Technologies and Consumer Brands.",
    "geography": "North America"
}

# @router.get("/breakdown/")
# async def breakdown():
#   return {"response": "hi"}

# # API route to interact with OpenAI API
# @router.post("/breakdown/")
# async def breakdown(request: ChatRequest):
#     system_message = f'''
#         You are assisting a user from the following context:
#         - Role: {person_details['role']}
#         - Company: {person_details['company']}
#         - Company Geography: {person_details['geography']}
        
#         Please provide responses based on the user's background.
        
#         The response must be in the following JSON format:
#         {{
#           "Goal": "one title line for what the user is trying to achieve",
#           "Questions": [
#             "your first question",
#             "your second question"
#           ]
#         }}
#     '''

#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {API_KEY}",
#     }

#     payload = {
#         "model": "gpt-3.5-turbo",
#         "messages": [
#             {"role": "system", "content": system_message},
#             {"role": "user", "content": request.content}
#         ],
#         "max_tokens": 200,
#         "temperature": 0.7
#     }

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
#             response.raise_for_status()
#             result = response.json()
#             response_text = result["choices"][0]["message"]["content"]
#             return {"response": response_text}
#     except httpx.HTTPError as http_err:
#         raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {http_err}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Pydantic model for the request body
class ChatRequest(BaseModel):
    content: str

# Mock data to be returned
mock_response = {
    "Goal": "Improve business operations efficiency",
    "Questions": [
        "What are the key challenges faced in the current operations?",
        "How can we optimize the supply chain processes?",
        "What technology solutions can be leveraged for automation?",
        "How can customer feedback be integrated into operational strategies?",
        "What are the potential cost-saving measures?"
    ]
}

@router.get("/breakdown/")
async def breakdown():
    return {"response": "hi"}

# Mock API route to return hardcoded responses
@router.post("/breakdown/")
async def breakdown(request: ChatRequest):
    return mock_response
