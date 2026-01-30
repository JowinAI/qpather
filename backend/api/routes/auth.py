from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from db import models, schemas
from api.dependencies.model_utils import get_db
from utils.email_service import send_email
import os
import bcrypt
from datetime import datetime, timedelta
import jwt

router = APIRouter()


SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-tokens-change-this-in-prod")
ALGORITHM = "HS256"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

class RegisterRequest(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    clientId: Optional[int] = None
    organizationId: Optional[int] = None
    organizationName: Optional[str] = None
    role: str
    department: Optional[str] = None
    bio: Optional[str] = None
    decisionStyle: Optional[str] = None
    objectives: Optional[List[str]] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SetPasswordRequest(BaseModel):
    token: str
    password: str

class DevLoginRequest(BaseModel):
    email: EmailStr

@router.post("/auth/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Check if user exists
    db_user = db.query(models.User).filter(models.User.Email == request.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Handle Client and Organization
    client_id = request.clientId
    org_id = request.organizationId
    
    # If no clientId provided, try to find by organizationName or organizationId
    if not client_id:
        if org_id:
            org = db.query(models.Organization).filter(models.Organization.Id == org_id).first()
            if org:
                client_id = org.ClientId
        elif request.organizationName:
            # Maybe the organizationName exists?
            org = db.query(models.Organization).filter(models.Organization.Name == request.organizationName).first()
            if org:
                client_id = org.ClientId
                org_id = org.Id
    
    # If still no client_id, use the first one (Default Client)
    client = None
    if client_id:
        client = db.query(models.Client).filter(models.Client.Id == client_id).first()
    
    if not client:
        client = db.query(models.Client).first()
        if not client:
            client = models.Client(Name="Default Client", CreatedBy="system")
            db.add(client)
            db.flush()
        client_id = client.Id

    # Domain Validation
    if client.AllowedDomains:
        allowed_domains = [d.strip().lower() for d in client.AllowedDomains.split(',')]
        user_domain = request.email.split('@')[-1].lower()
        if user_domain not in allowed_domains and client.Name != "TEST":
            raise HTTPException(
                status_code=400, 
                detail=f"Your email domain '{user_domain}' is not recognized for this client. Please contact your administrator."
            )

    # Handle Organization setup
    if not org_id and request.organizationName:
        new_org = models.Organization(
            ClientId=client_id,
            Name=request.organizationName,
            CreatedBy="registration"
        )
        db.add(new_org)
        db.flush()
        org_id = new_org.Id
    
    if not org_id:
        # Link to the first organization of the client
        first_org = db.query(models.Organization).filter(models.Organization.ClientId == client_id).first()
        if first_org:
            org_id = first_org.Id
        else:
            # Create a default org for the client
            new_org = models.Organization(
                ClientId=client_id,
                Name=f"{client.Name} Default",
                CreatedBy="registration"
            )
            db.add(new_org)
            db.flush()
            org_id = new_org.Id

    # 4. Auto-Approval Logic
    user_status = 'PENDING_APPROVAL'
    if client.AutoApprove:
        user_status = 'ACTIVE'


    # 3. Handle Department
    dept_id = None
    if request.department and org_id:
        dept = db.query(models.Department).filter(
            models.Department.Name == request.department,
            models.Department.OrganizationId == org_id
        ).first()
        if not dept:
            dept = models.Department(
                Name=request.department,
                OrganizationId=org_id,
                CreatedBy="registration"
            )
            db.add(dept)
            db.flush()
        dept_id = dept.Id
    
    # 4. Create User
    new_user = models.User(
        OrganizationId=org_id,
        DepartmentId=dept_id,
        FirstName=request.firstName,
        LastName=request.lastName,
        Email=request.email,
        Role=request.role,
        Bio=request.bio,
        DecisionStyle=request.decisionStyle,
        Status=user_status,
        CreatedBy="self_signup"
    )
    db.add(new_user)
    db.flush()

    # 5. Create UserSettings if objectives provided
    if request.objectives:
        new_settings = models.UserSettings(
            UserId=new_user.Id,
            BusinessObjective=", ".join(request.objectives),
            CreatedBy="self_signup"
        )
        db.add(new_settings)

    db.commit()

    # 5. Send Notification Email to User
    if user_status == 'ACTIVE':
        # Generate activation token immediately
        token = jwt.encode({"sub": request.email, "type": "activation", "exp": datetime.utcnow() + timedelta(days=7)}, SECRET_KEY, algorithm=ALGORITHM)
        activation_link = f"{FRONTEND_URL}/auth/activate?token={token}"
        
        subject = "Access Approved! Welcome to Dooe AI"
        html_body = f"""
        <html>
            <body>
                <h2>Access Approved!</h2>
                <p>Hi {request.firstName},</p>
                <p>Your account has been automatically approved. Click the link below to set your password and get started:</p>
                <p><a href="{activation_link}">Set Password & Activate Account</a></p>
            </body>
        </html>
        """
    else:
        subject = "Welcome to Dooe AI - Registration Received"
        html_body = f"""
        <html>
            <body>
                <h2>Welcome to Dooe AI!</h2>
                <p>Hi {request.firstName},</p>
                <p>Thank you for joining Dooe AI. Your account is currently <strong>Pending Approval</strong> by your organization administrators.</p>
                <p>Once approved, you will receive another email with instructions to set your password.</p>
            </body>
        </html>
        """
    
    try:
        await send_email(subject, [request.email], html_body)
    except Exception as e:
        print(f"Error sending registration email: {e}")

    return {
        "message": "User registered successfully", 
        "status": user_status,
        "userId": new_user.Id
    }

@router.post("/auth/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.Email == request.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.Status != 'ACTIVE':
        raise HTTPException(status_code=403, detail=f"User status is {db_user.Status}. Please wait for approval.")
    
    if not db_user.PasswordHash:
         raise HTTPException(status_code=403, detail="Password not set. Please use the activation link sent to your email.")

    password_bytes = request.password.encode('utf-8')
    hash_bytes = db_user.PasswordHash.encode('utf-8')
    if not bcrypt.checkpw(password_bytes, hash_bytes):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate Token
    access_token_expires = timedelta(minutes=60)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"sub": db_user.Email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "user": {
            "id": db_user.Id,
            "email": db_user.Email,
            "firstName": db_user.FirstName,
            "lastName": db_user.LastName,
            "role": db_user.Role,
            "status": db_user.Status,
            "organizationId": db_user.OrganizationId,
            "departmentId": db_user.DepartmentId
        }
    }

@router.post("/auth/approve")
async def approve_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.Id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.Status = 'ACTIVE' # Note: In a real flow, you might keep it as PENDING till password set, but BRD says Approve -> Active
    db.commit()

    # Generate a one-time activation token
    token = jwt.encode({"sub": db_user.Email, "type": "activation", "exp": datetime.utcnow() + timedelta(days=7)}, SECRET_KEY, algorithm=ALGORITHM)
    activation_link = f"{FRONTEND_URL}/auth/activate?token={token}"

    subject = "You're In! Welcome to Dooe AI"
    html_body = f"""
    <html>
        <body>
            <h2>Access Approved!</h2>
            <p>Hi {db_user.FirstName},</p>
            <p>Your account has been approved. Please click the link below to set your password and start using Dooe AI:</p>
            <p><a href="{activation_link}">Set Password & Activate Account</a></p>
        </body>
    </html>
    """
    print(f"DEBUG: Activation link for {db_user.Email}: {activation_link}")
    try:
        await send_email(subject, [db_user.Email], html_body)
    except Exception as e:
        print(f"Error sending approval email: {e}")
    return {"message": "User approved and activation email sent"}

@router.post("/auth/activate")
async def activate_account(request: SetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email or payload.get("type") != "activation":
            raise HTTPException(status_code=400, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

    db_user = db.query(models.User).filter(models.User.Email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
    db_user.PasswordHash = hashed_password.decode('utf-8')
    db_user.Status = 'ACTIVE'
    db.commit()

    return {"message": "Password set successfully. You can now login."}

@router.post("/auth/dev-login")
async def dev_login(request: DevLoginRequest, db: Session = Depends(get_db)):
    # For Internal/Dev use only: Login without password checks
    db_user = db.query(models.User).filter(models.User.Email == request.email).first()
    
    # Auto-Provisioning for Dev Environment
    if not db_user:
        # Find default organization or create one
        org = db.query(models.Organization).first()
        if not org:
            # Create minimal structure if DB is empty
            client = models.Client(Name="Default Client", CreatedBy="system")
            db.add(client)
            db.flush()
            org = models.Organization(ClientId=client.Id, Name="Default Organization", CreatedBy="system")
            db.add(org)
            db.flush()
            
        # Create new active user
        first_name = request.email.split('@')[0]
        db_user = models.User(
            OrganizationId=org.Id,
            FirstName=first_name.capitalize(),
            LastName="User",
            Email=request.email,
            Role="Contributor",
            Status="ACTIVE",
            CreatedBy="dev_login",
            Bio="Auto-created via Dev Login"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    # Generate Token
    access_token_expires = timedelta(minutes=60)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"sub": db_user.Email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "user": {
            "id": db_user.Id,
            "email": db_user.Email,
            "firstName": db_user.FirstName,
            "lastName": db_user.LastName,
            "role": db_user.Role,
            "status": db_user.Status,
            "organizationId": db_user.OrganizationId,
            "departmentId": db_user.DepartmentId
        }
    }
