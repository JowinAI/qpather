from pydantic import BaseModel, EmailStr, condecimal
from typing import Optional, List, Union
from datetime import datetime

# Client Schema
class ClientBase(BaseModel):
    Name: str
    ContactEmail: Optional[EmailStr] = None
    ContactPhone: Optional[str] = None
    Address: Optional[str] = None
    Status: Optional[str] = 'Active'
    AutoApprove: Optional[bool] = False
    AllowedDomains: Optional[str] = None
    WebsiteUrl: Optional[str] = None
    CompanySummary: Optional[str] = None
    Industry: Optional[str] = None
    PrimaryGoals: Optional[str] = None
    Notes: Optional[str] = None
    LogoUrl: Optional[str] = None
    PrimaryColor: Optional[str] = None
    SecondaryColor: Optional[str] = None
    DisplayNameShort: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    UpdatedBy: Optional[str] = None

class Client(ClientBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: Optional[str]
    UpdatedBy: Optional[str]

    class Config:
        from_attributes = True


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
    CreatedBy: Optional[str]
    UpdatedBy: Optional[str]

    class Config:
        from_attributes = True


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
    CreatedBy: Optional[str]
    UpdatedBy: Optional[str]

    class Config:
        from_attributes = True


# User Schema
class UserBase(BaseModel):
    OrganizationId: Optional[int] = None
    DepartmentId: Optional[int] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Email: EmailStr
    Role: Optional[str] = None
    Bio: Optional[str] = None
    DecisionStyle: Optional[str] = None
    Status: Optional[str] = 'PENDING_APPROVAL'

class UserCreate(UserBase):
    CreatedBy: str
    Password: Optional[str] = None

class UserUpdate(UserBase):
    UpdatedBy: Optional[str] = None

class User(UserBase):
    Id: int
    Status: Optional[str] = 'ACTIVE'
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: Optional[str]
    UpdatedBy: Optional[str]
    OrganizationName: Optional[str] = None
    DepartmentName: Optional[str] = None

    class Config:
        from_attributes = True


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
        from_attributes = True

    class Config:
        from_attributes = True


# Assignment Schema
class AssignmentBase(BaseModel):
    GoalId: int
    ParentAssignmentId: Optional[int] = None
    QuestionText: str
    Order: Optional[int] = None

class AssignmentCreate(AssignmentBase):
    CreatedBy: str
    CreatedAt: Optional[datetime] = None
    ThreadId: Optional[str] = None

class AssignmentUpdate(AssignmentBase):
    UpdatedBy: Optional[str] = None
    # Add fields that should be updatable but are not in Base if any
    pass

class Assignment(AssignmentBase):
    Id: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]
    ThreadId: Optional[str] = None

    class Config:
        from_attributes = True

class InviteeDetail(BaseModel):
    Email: EmailStr
    FirstName: str
    LastName: str
    Role: Optional[str] = None
    
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
    Invitees: List[InviteeDetail] = [] # List of new invitees
    ThreadId: Optional[str] = None
   
class AssignmentsFirstSave(BaseModel):
    Assignments:List[AssignmentWithUsers] 
    Goal:str
    GoalDescription:Optional[str] = None
    OrganizationId:Optional[int] =None
    DueDate:Optional[datetime]=None
    InitiatedBy:Optional[str]=None  





class UserResponseBase(BaseModel):
    AssignmentId: int
    AssignedTo: str
    Answer: Optional[str] = None
    Attachments: Optional[str] = None
    Status: Optional[str] = 'Assigned'
    CreatedBy: Optional[str] = None

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
    ThreadId: Optional[str] = None

    class Config:
        from_attributes = True


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
        from_attributes = True


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
        from_attributes = True


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
        from_attributes = True


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
        from_attributes = True


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
        from_attributes = True


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
        from_attributes = True


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
        from_attributes = True


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
        from_attributes = True


# Schema for user details used in assignments
class AssignmentUser(BaseModel):
    id: Union[str, int]  # Allow string IDs for new/temp users
    name: str
    email: EmailStr

# Schema for questions within a goal
class Question(BaseModel):
    text: str
    assigned_users: List[AssignmentUser]

# GoalWithAssignments schema for incoming goal data with assignments
class GoalWithAssignments(BaseModel):
    goal_id: Optional[int] = None
    title: str
    description: str
    due_date: Optional[datetime] = None
    department_id: int
    organization_id: int
    created_by: AssignmentUser
    questions: List[Question]

# Response schema for goal creation with assignments
class GoalResponse(BaseModel):
    Goal: str
    Assignments: List[AssignmentWithUsers]

    class Config:
        from_attributes = True
class UserResponseDetail(BaseModel):
    AssignedTo: str
    Name: Optional[str] = None
    Answer: Optional[str] = None
    Attachments: Optional[str] = None
    Status: str
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    ThreadId: Optional[str] = None


class AssignmentDetails(BaseModel):
    Id: int
    ParentAssignmentId: Optional[int]
    QuestionText: str
    Order: Optional[int]
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedBy: str
    UpdatedBy: Optional[str]
    ThreadId: Optional[str] = None
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
    ThreadId: Optional[str] = None
    Assignments: List[AssignmentDetails]


class GoalSummary(BaseModel):
    Id: int
    Title: str
    DueDate: str  # Formatted as string to display properly
    Status: str
    AssignedUsers: List[str]  # List of assigned user emails
    CreatedBy: str  # Creator's email
    ViewLink: str

    class Config:
        from_attributes = True

class PaginatedGoalSummary(BaseModel):
    total: int
    items: List[GoalSummary]    

class AssignmentWithStatus(Assignment):
    Status: str
    Answer: Optional[str] = None    
    Attachments: Optional[str] = None
    DelegatedUsers: List[str] = []

# Delegated Assignment Create Schema
class DelegatedAssignmentCreate(BaseModel):
    GoalId: int
    ParentAssignmentId: Optional[int]
    QuestionText: str
    AssignedToEmail: EmailStr
    CreatedBy: str

# Invitation Schema
class InvitationBase(BaseModel):
    Email: EmailStr
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Role: Optional[str] = None
    GoalId: int
    QuestionText: str

class InvitationCreate(InvitationBase):
    CreatedBy: str

class Invitation(InvitationBase):
    Id: int
    Token: str
    ExpiresAt: datetime
    Used: bool
    CreatedAt: datetime
    CreatedBy: str
    
    class Config:
        from_attributes = True

# Dashboard Settings Schemas
class DashboardSections(BaseModel):
    executiveSummary: bool = True
    signalHealth: bool = True
    topRisks: bool = True
    conflicts: bool = True
    patterns: bool = True
    actions: bool = True
    dataGaps: bool = True
    evidence: bool = False
    focusQna: bool = True

class DashboardDisplay(BaseModel):
    timeHorizon: str = "next_2_3_quarters"
    verbosity: str = "concise"
    maxRisks: int = 5
    maxActions: int = 5

class FocusQuestionRules(BaseModel):
    maxQuestions: int = 5
    maxChars: int = 120
    answerStyle: str = "2-3 bullets"
    mustReferenceSources: bool = True

class DashboardSettingsPayload(BaseModel):
    lensName: str
    focusSignals: List[str]
    focusQuestions: List[str]
    sections: DashboardSections
    display: DashboardDisplay
    focusQuestionRules: Optional[FocusQuestionRules] = None

class DashboardSettings(BaseModel):
    Id: int
    UserId: int
    GoalId: Optional[int]
    Settings: str # JSON String
    
    class Config:
        from_attributes = True

# Goal Dashboard Insight Schema
class GoalDashboardInsight(BaseModel):
    Id: int
    GoalId: int
    UserId: Optional[int]
    LensSignature: Optional[str]
    InsightJson: str
    ModelUsed: Optional[str]
    PromptVersion: Optional[str]
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]

    class Config:
        from_attributes = True

# Analysis Request Models
class ViewerContext(BaseModel):
    name: str
    email: str
    role: str

class GoalContext(BaseModel):
    goal_id: str
    goal_title: str
    goal_text: str
    as_of_date: str

class HierarchyNode(BaseModel):
    node_id: str
    level: int
    parent_id: Optional[str] = None
    signal: Optional[dict] = None # {name: str, type: str}
    assigned_to: Optional[dict] = None # {name, email, role}
    question: str
    responses: List[dict] # [{response_id, from, text, confidence}]

class HierarchyData(BaseModel):
    nodes: List[HierarchyNode]

class AnalysisRules(BaseModel):
    signal_weighting: dict
    status_thresholds: dict

class AnalysisRequest(BaseModel):
    viewer_context: ViewerContext
    goal_context: GoalContext
    dashboard_request: DashboardSettingsPayload # Reuse existing
    hierarchy: HierarchyData
    rules: Optional[AnalysisRules] = None

# Chat Request Models
class ChatRequest(BaseModel):
    viewer_context: ViewerContext
    goal_context: GoalContext
    dashboard_request: DashboardSettingsPayload
    hierarchy: HierarchyData
    insight_snapshot: dict # JSON of the analysis
    user_question: str



class EnhanceRequest(BaseModel):
    text: str


class BreakdownRequest(BaseModel):
    content: str


# RawContextInput Schema
class RawContextInputBase(BaseModel):
    GoalId: int
    Content: str
    Attachments: Optional[str] = None

class RawContextInputCreate(RawContextInputBase):
    UserEmail: str

class RawContextInput(RawContextInputBase):
    Id: int
    UserId: int
    CreatedAt: datetime
    
    class Config:
        from_attributes = True


