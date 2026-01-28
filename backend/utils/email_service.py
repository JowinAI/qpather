from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic_settings import BaseSettings
from pydantic import EmailStr
import os
from dotenv import load_dotenv

load_dotenv()

class MailConfig(BaseSettings):
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "no-reply@dooe.ai")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: EmailStr = os.getenv("MAIL_FROM", "no-reply@dooe.ai")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

conf = ConnectionConfig(
    MAIL_USERNAME=MailConfig().MAIL_USERNAME,
    MAIL_PASSWORD=MailConfig().MAIL_PASSWORD,
    MAIL_FROM=MailConfig().MAIL_FROM,
    MAIL_PORT=MailConfig().MAIL_PORT,
    MAIL_SERVER=MailConfig().MAIL_SERVER,
    MAIL_STARTTLS=MailConfig().MAIL_STARTTLS,
    MAIL_SSL_TLS=MailConfig().MAIL_SSL_TLS,
    USE_CREDENTIALS=MailConfig().USE_CREDENTIALS,
    VALIDATE_CERTS=MailConfig().VALIDATE_CERTS
)

async def send_email(subject: str, recipients: list, html_body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=html_body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
