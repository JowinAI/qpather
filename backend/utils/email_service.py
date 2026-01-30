# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic_settings import BaseSettings
from pydantic import EmailStr
import os
from dotenv import load_dotenv

load_dotenv()

# Simplified Mock Email Service due to library issues
async def send_email(subject: str, recipients: list, html_body: str):
    print(f"=======================================")
    print(f"MOCK EMAIL SENT")
    print(f"To: {recipients}")
    print(f"Subject: {subject}")
    print(f"Body (truncated): {html_body[:50]}...")
    print(f"=======================================")
    return True
