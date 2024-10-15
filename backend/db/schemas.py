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


# Goal Schema
class GoalBase(BaseModel):
    OrganizationId: int
    Title: str
    Date: datetime
    InitiatedBy: Optional[str] = None
    GoalDescription: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(GoalBase):
    UpdatedBy: Optional[str] = None

class Goal(GoalBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# Assignment Schema
class AssignmentBase(BaseModel):
    GoalId: int
    ParentAssignmentId: Optional[int] = None
    QuestionText: str
    Order: Optional[int] = None

class AssignmentCreate(AssignmentBase):
    pass

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


# AssignmentUser Schema
class AssignmentUserBase(BaseModel):
    AssignmentId: int
    AssignedTo: str

class AssignmentUserCreate(AssignmentUserBase):
    pass

class AssignmentUser(AssignmentUserBase):
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]

    class Config:
        orm_mode = True


# Response Schema
class ResponseBase(BaseModel):
    AssignmentId: int
    Answer: str

class ResponseCreate(ResponseBase):
    pass

class ResponseUpdate(ResponseBase):
    UpdatedBy: Optional[str] = None

class Response(ResponseBase):
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
    pass

    class Config:
        orm_mode = True


# AuditLog Schema
class AuditLogBase(BaseModel):
    UserId: Optional[int] = None
    OrganizationId: Optional[int] = None
    Action: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    Id: int
    Timestamp: datetime

    class Config:
        orm_mode = True
