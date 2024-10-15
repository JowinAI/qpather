from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, DECIMAL, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Client Table
class Client(Base):
    __tablename__ = 'client'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(255), nullable=False)
    ContactEmail = Column(String(255))
    ContactPhone = Column(String(50))
    Address = Column(String(255))
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)

# Organization Table
class Organization(Base):
    __tablename__ = 'organization'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('client.Id'), nullable=False)
    Name = Column(String(255), nullable=False)
    Address = Column(String(255))
    ContactEmail = Column(String(255))
    ContactPhone = Column(String(50))
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    client = relationship("Client")

# Department Table
class Department(Base):
    __tablename__ = 'department'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    OrganizationId = Column(Integer, ForeignKey('organization.Id'), nullable=False)
    Name = Column(String(255), nullable=False)
    ManagerName = Column(String(255))
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    organization = relationship("Organization")

# User Table
class User(Base):
    __tablename__ = 'user'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    OrganizationId = Column(Integer, ForeignKey('organization.Id'), nullable=True)
    DepartmentId = Column(Integer, ForeignKey('department.Id'), nullable=True)
    FirstName = Column(String(100))
    LastName = Column(String(100))
    Email = Column(String(255), unique=True, nullable=False)
    Role = Column(String(50))
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    organization = relationship("Organization")
    department = relationship("Department")

# Goal Table
class Goal(Base):
    __tablename__ = 'goal'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    OrganizationId = Column(Integer, ForeignKey('organization.Id'), nullable=False)
    Title = Column(String(255), nullable=False)
    Date = Column(DateTime, nullable=False)
    InitiatedBy = Column(String(255))
    GoalDescription = Column(String(255))
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    organization = relationship("Organization")

# Assignment Table
class Assignment(Base):
    __tablename__ = 'assignment'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    GoalId = Column(Integer, ForeignKey('goal.Id'), nullable=False)
    ParentAssignmentId = Column(Integer, ForeignKey('assignment.Id'), nullable=True)
    QuestionText = Column(String(255), nullable=False)
    Order = Column(Integer)
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    goal = relationship("Goal")
    parent_assignment = relationship("Assignment", remote_side=[Id])

# AssignmentUser Table
class AssignmentUser(Base):
    __tablename__ = 'assignment_user'
    
    AssignmentId = Column(Integer, ForeignKey('assignment.Id'), primary_key=True)
    AssignedTo = Column(String(255), primary_key=True)  # Composite primary key
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    assignment = relationship("Assignment")

# Response Table
class Response(Base):
    __tablename__ = 'response'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    AssignmentId = Column(Integer, ForeignKey('assignment.Id'), nullable=False)
    Answer = Column(Text, nullable=False)
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    assignment = relationship("Assignment")

# OrganizationSettings Table
class OrganizationSettings(Base):
    __tablename__ = 'organization_settings'
    
    OrganizationId = Column(Integer, ForeignKey('organization.Id'), primary_key=True)
    BusinessSector = Column(String(100))
    CompanySize = Column(String(50))
    TeamStructure = Column(Text)
    GeographicFocus = Column(Text)
    HistoricalData = Column(Text)
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    organization = relationship("Organization")

# UserSettings Table
class UserSettings(Base):
    __tablename__ = 'user_settings'
    
    UserId = Column(Integer, ForeignKey('user.Id'), primary_key=True)
    Role = Column(String(255))
    BusinessObjective = Column(Text)
    CurrentChallenges = Column(Text)
    KPIs = Column(Text)
    TeamMemberRoles = Column(Text)
    PriorityLevel = Column(String(50))
    LevelOfComplexity = Column(String(50))
    TargetOutcome = Column(Text)
    CommunicationStyle = Column(String(50))
    GoalTimeframe = Column(String(50))
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    user = relationship("User")

# SubscriptionPlan Table
class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plan'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    PlanName = Column(String(100), nullable=False)
    Price = Column(DECIMAL(10, 2), nullable=False)
    Features = Column(Text)
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)

# OrganizationSubscription Table
class OrganizationSubscription(Base):
    __tablename__ = 'organization_subscription'
    
    OrganizationId = Column(Integer, ForeignKey('organization.Id'), primary_key=True)
    SubscriptionPlanId = Column(Integer, ForeignKey('subscription_plan.Id'), primary_key=True)
    StartDate = Column(DateTime, nullable=False)
    EndDate = Column(DateTime, nullable=False)
    IsActive = Column(Boolean, default=True)
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    organization = relationship("Organization")
    subscription_plan = relationship("SubscriptionPlan")

# Billing Table
class Billing(Base):
    __tablename__ = 'billing'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    OrganizationId = Column(Integer, ForeignKey('organization.Id'), nullable=False)
    Amount = Column(DECIMAL(10, 2), nullable=False)
    BillingPeriodStart = Column(DateTime)
    BillingPeriodEnd = Column(DateTime)
    Status = Column(String(50))
    PaymentDate = Column(DateTime)
    CreatedAt = Column(DateTime, default=func.now())
    UpdatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    CreatedBy = Column(String(255))
    UpdatedBy = Column(String(255), nullable=True)
    
    organization = relationship("Organization")

# Feature Table
class Feature(Base):
    __tablename__ = 'feature'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    FeatureName = Column(String(100), nullable=False)
    Description = Column(Text)

# OrganizationFeatureAccess Table
class OrganizationFeatureAccess(Base):
    __tablename__ = 'organization_feature_access'
    
    OrganizationId = Column(Integer, ForeignKey('organization.Id'), primary_key=True)
    FeatureId = Column(Integer, ForeignKey('feature.Id'), primary_key=True)
    AccessGranted = Column(Boolean, default=True)
    
    organization = relationship("Organization")
    feature = relationship("Feature")

# AuditLog Table
class AuditLog(Base):
    __tablename__ = 'audit_log'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey('user.Id'))
    OrganizationId = Column(Integer, ForeignKey('organization.Id'))
    Action = Column(String(255))
    Timestamp = Column(DateTime, default=func.now())
    
    user = relationship("User")
    organization = relationship("Organization")
