from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from utils.email_service import send_email
import os

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

class EmailRequest(BaseModel):
    email: EmailStr
    name: str

class ApprovalRequest(BaseModel):
    user_id: str
    email: EmailStr
    name: str

@router.post("/send-verification")
async def send_verification_email(request: EmailRequest):
    """
    Sends an email to the user that their registration is pending admin approval.
    """
    subject = "Welcome to DOOE AI - Registration Received"
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #2563EB;">Welcome to DOOE AI!</h2>
                <p>Hi {request.name},</p>
                <p>Thank you for joining <strong>DOOE AI</strong>, the intelligent platform for strategic planning and execution.</p>
                
                <div style="background-color: #F3F4F6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Status:</strong> <span style="color: #D97706;">Pending Approval</span></p>
                    <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #666;">Your request has been sent to your organization's administrators.</p>
                </div>

                <p><strong>What happens next?</strong></p>
                <ul style="color: #555;">
                    <li>An admin will review your access request.</li>
                    <li>Once approved, you will receive a confirmation email.</li>
                    <li>You'll then be able to log in and start collaborating.</li>
                </ul>

                <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.8em; color: #888; text-align: center;">
                    &copy; 2024 DOOE AI. All rights reserved.<br>
                    <a href="{FRONTEND_URL}" style="color: #2563EB; text-decoration: none;">Visit Dashboard</a>
                </p>
            </div>
        </body>
    </html>
    """
    try:
        await send_email(subject, [request.email], html_body)
        return {"message": "Verification email sent"}
    except Exception as e:
        print(f"\n[EMAIL SIMULATION] Failed to send real email ({e}).")
        print(f"To: {request.email}")
        print(f"Subject: {subject}")
        print(f"Content: Account Pending Approval\n")
        return {"message": "Email simulation: Verification email logged"}

@router.post("/approve-user")
async def approve_user_email(request: ApprovalRequest):
    """
    Sends an approval email with activation/login link to the user.
    """
    login_link = f"{FRONTEND_URL}/login" 
    
    subject = "You're In! Welcome to DOOE AI"
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
             <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #16A34A;">Access Approved!</h2>
                <p>Hi {request.name},</p>
                <p>Good news! Your account access for <strong>DOOE AI</strong> has been approved.</p>
                
                <p>You can now access your dashboard to:</p>
                <ul style="color: #555;">
                    <li>Create and track strategic goals</li>
                    <li>Collaborate with your team</li>
                    <li>Visualize performance metrics</li>
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_link}" style="background-color: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        Login to DOOE AI
                    </a>
                </div>
                
                <p style="font-size: 0.9em; text-align: center; color: #666;">
                    Or copy this link: <a href="{login_link}">{login_link}</a>
                </p>

                <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.8em; color: #888; text-align: center;">
                    &copy; 2024 DOOE AI. All rights reserved.
                </p>
            </div>
        </body>
    </html>
    """
    try:
        await send_email(subject, [request.email], html_body)
        return {"message": "Approval email sent"}
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"[EMAIL SIMULATION] SMTP Error: {e}")
        print(f"To: {request.email}")
        print(f"Subject: {subject}")
        print(f"ACTION REQUIRED: Click the link below to verify the flow:")
        print(f"\nUser Login Link: {login_link}")
        print(f"{'='*60}\n")
        return {"message": "Email simulation: Approval email logged"}
