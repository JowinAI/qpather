from pydantic import BaseModel, EmailStr, condecimal
from typing import Optional, List
from datetime import datetime

# Client Schema
class ClientBase(BaseModel):
    Name: str
    ContactEmail: Optional[EmailStr] = None
    ContactPhone: Optional[str] = None
    Address: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    UpdatedBy: Optional[str] = None

class Client(ClientBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# Organization Schema
class OrganizationBase(BaseModel):
    ClientId: int
    Name: str
    Address: Optional[str] = None
    ContactEmail: Optional[EmailStr] = None
    ContactPhone: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    UpdatedBy: Optional[str] = None

class Organization(OrganizationBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# Department Schema
class DepartmentBase(BaseModel):
    OrganizationId: int
    Name: str
    ManagerName: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    UpdatedBy: Optional[str] = None

class Department(DepartmentBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# User Schema
class UserBase(BaseModel):
    OrganizationId: Optional[int] = None
    DepartmentId: Optional[int] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Email: EmailStr
    Role: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    UpdatedBy: Optional[str] = None

class User(UserBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# Goal Schema (DueDate instead of Date)
class GoalBase(BaseModel):
    OrganizationId: int
    Title: str
    DueDate: Optional[datetime] 
    InitiatedBy: Optional[str] = None
    GoalDescription: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(GoalBase):
    UpdatedBy: Optional[str] = None

class Goal(BaseModel):
    Id: int
    OrganizationId: int
    Title: str
    DueDate: Optional[datetime]  # Allow None values for DueDate
    InitiatedBy: Optional[str]
    GoalDescription: Optional[str]
    CreatedAt: datetime
    UpdatedAt: datetime
    CreatedBy: Optional[str]
    UpdatedBy: Optional[str]
    DepartmentId: Optional[int]

    class Config:
        orm_mode = True

    class Config:
        orm_mode = True


# Assignment Schema
class AssignmentBase(BaseModel):
    GoalId: int
    ParentAssignmentId: Optional[int] = None
    QuestionText: str
    Order: Optional[int] = None
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
    CreatedBy: str
    UpdatedBy: Optional[str] = None

class AssignmentCreate(AssignmentBase):
    pass

    
class AssignmentWithUsers(BaseModel):
    Id: Optional[int] = None
    GoalId: Optional[int] = None
    Goal:Optional[str] = None
    ParentAssignmentId: Optional[int] = None
    QuestionText: str
    Order: Optional[int] = None
    CreatedAt: datetime = datetime.utcnow()  # Default value
    UpdatedAt: Optional[datetime] = None
    CreatedBy: str
    UpdatedBy: Optional[str] = None
    AssignedUsers: List[str]  = None# List of assigned users
   
class AssignmentsFirstSave(BaseModel):
    Assignments:List[AssignmentWithUsers] 
    Goal:str
    GoalDescription:Optional[str] = None
    OrganizationId:Optional[int] =None
    DueDate:Optional[datetime]=None
    InitiatedBy:Optional[str]=None  


class AssignmentUpdate(AssignmentBase):
    UpdatedBy: Optional[str] = None

class Assignment(AssignmentBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


class UserResponseBase(BaseModel):
    AssignmentId: int
    AssignedTo: str
    Answer: Optional[str] = None
    Status: Optional[str] = 'Assigned'

class UserResponseCreate(UserResponseBase):
    pass

class UserResponseUpdate(UserResponseBase):
    UpdatedBy: Optional[str] = None

class UserResponse(UserResponseBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# OrganizationSettings Schema
class OrganizationSettingsBase(BaseModel):
    OrganizationId: int
    BusinessSector: Optional[str] = None
    CompanySize: Optional[str] = None
    TeamStructure: Optional[str] = None
    GeographicFocus: Optional[str] = None
    HistoricalData: Optional[str] = None

class OrganizationSettingsCreate(OrganizationSettingsBase):
    pass

class OrganizationSettingsUpdate(OrganizationSettingsBase):
    UpdatedBy: Optional[str] = None

class OrganizationSettings(OrganizationSettingsBase):
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# UserSettings Schema
class UserSettingsBase(BaseModel):
    UserId: int
    Role: Optional[str] = None
    BusinessObjective: Optional[str] = None
    CurrentChallenges: Optional[str] = None
    KPIs: Optional[str] = None
    TeamMemberRoles: Optional[str] = None
    PriorityLevel: Optional[str] = None
    LevelOfComplexity: Optional[str] = None
    TargetOutcome: Optional[str] = None
    CommunicationStyle: Optional[str] = None
    GoalTimeframe: Optional[str] = None

class UserSettingsCreate(UserSettingsBase):
    pass

class UserSettingsUpdate(UserSettingsBase):
    UpdatedBy: Optional[str] = None

class UserSettings(UserSettingsBase):
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# SubscriptionPlan Schema
class SubscriptionPlanBase(BaseModel):
    PlanName: str
    Price: condecimal(max_digits=10, decimal_places=2)
    Features: Optional[str] = None

class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass

class SubscriptionPlanUpdate(SubscriptionPlanBase):
    UpdatedBy: Optional[str] = None

class SubscriptionPlan(SubscriptionPlanBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# OrganizationSubscription Schema
class OrganizationSubscriptionBase(BaseModel):
    OrganizationId: int
    SubscriptionPlanId: int
    StartDate: datetime
    EndDate: datetime
    IsActive: bool

class OrganizationSubscriptionCreate(OrganizationSubscriptionBase):
    pass

class OrganizationSubscription(OrganizationSubscriptionBase):
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# Billing Schema
class BillingBase(BaseModel):
    OrganizationId: int
    Amount: condecimal(max_digits=10, decimal_places=2)
    BillingPeriodStart: Optional[datetime] = None
    BillingPeriodEnd: Optional[datetime] = None
    Status: Optional[str] = None
    PaymentDate: Optional[datetime] = None

class BillingCreate(BillingBase):
    pass

class BillingUpdate(BillingBase):
    UpdatedBy: Optional[str] = None

class Billing(BillingBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# Feature Schema
class FeatureBase(BaseModel):
    FeatureName: str
    Description: Optional[str] = None

class FeatureCreate(FeatureBase):
    pass

class FeatureUpdate(FeatureBase):
    pass

class Feature(FeatureBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# OrganizationFeatureAccess Schema
class OrganizationFeatureAccessBase(BaseModel):
    OrganizationId: int
    FeatureId: int
    AccessGranted: bool = True

class OrganizationFeatureAccessCreate(OrganizationFeatureAccessBase):
    pass

class OrganizationFeatureAccessUpdate(OrganizationFeatureAccessBase):
    pass

class OrganizationFeatureAccess(OrganizationFeatureAccessBase):
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# AuditLog Schema
class AuditLogBase(BaseModel):
    UserId: Optional[str] = None  # Changed to string (email) instead of FK
    OrganizationId: Optional[int] = None
    Action: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    Id: int
    Timestamp: datetime

    class Config:
        orm_mode = True


# Schema for user details used in assignments
class AssignmentUser(BaseModel):
    id: int
    name: str
    email: EmailStr

# Schema for questions within a goal
class Question(BaseModel):
    text: str
    assigned_users: List[AssignmentUser]

# GoalWithAssignments schema for incoming goal data with assignments
class GoalWithAssignments(BaseModel):
    title: str
    description: str
    due_date: datetime
    department_id: int
    organization_id: int
    created_by: AssignmentUser
    questions: List[Question]

# Response schema for goal creation with assignments
class GoalResponse(BaseModel):
    Goal: str
    Assignments: List[AssignmentWithUsers]

    class Config:
        orm_mode = True
class UserResponseDetail(BaseModel):
    AssignedTo: str
    Answer: Optional[str] = None
    Status: str
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]


class AssignmentDetails(BaseModel):
    Id: int
    ParentAssignmentId: Optional[int]
    QuestionText: str
    Order: Optional[int]
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]
    UserResponses: List[UserResponseDetail]

class GoalDetailsResponse(BaseModel):
    Id: int
    Title: str
    DueDate: Optional[datetime] 
    GoalDescription: Optional[str]
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]
    Assignments: List[AssignmentDetails]


class GoalSummary(BaseModel):
    Id: int
    Title: str
    DueDate: str  # Formatted as string to display properly
    Status: str
    AssignedUsers: List[str]  # List of assigned user emails
    ViewLink: str

    class Config:
        orm_mode = True

class PaginatedGoalSummary(BaseModel):
    total: int
    items: List[GoalSummary]    
