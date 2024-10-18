-- Drop existing tables if they exist
--DROP TABLE IF EXISTS OrganizationFeatureAccess, Feature, AuditLog, Billing, OrganizationSubscription, SubscriptionPlan, UserSettings, OrganizationSettings, UserResponse, Assignment, Goal, [User], Department, Organization, Client;

-- Client Table
CREATE TABLE Client (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(255) NOT NULL,                 -- Name of the client company
    ContactEmail NVARCHAR(255),                  -- Client's contact email
    ContactPhone NVARCHAR(50),                   -- Client's contact phone number
    Address NVARCHAR(255),                       -- Client's address
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL                 -- Audit column
);

-- Organization Table
CREATE TABLE Organization (
    Id INT PRIMARY KEY IDENTITY(1,1),
    ClientId INT NOT NULL,                       -- Foreign key to Client
    Name NVARCHAR(255) NOT NULL,                 -- Organization's name
    Address NVARCHAR(255),
    ContactEmail NVARCHAR(255),
    ContactPhone NVARCHAR(50),
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (ClientId) REFERENCES Client(Id)
);

-- Department Table
CREATE TABLE Department (
    Id INT PRIMARY KEY IDENTITY(1,1),
    OrganizationId INT NOT NULL,                 -- Foreign key to Organization
    Name NVARCHAR(255) NOT NULL,                 -- Department's name
    ManagerName NVARCHAR(255),                   -- Department manager
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (OrganizationId) REFERENCES Organization(Id)
);

-- User Table
CREATE TABLE [User] (
    Id INT PRIMARY KEY IDENTITY(1,1),
    OrganizationId INT,                          -- Foreign key to Organization
    DepartmentId INT NULL,                       -- Nullable foreign key to Department
    FirstName NVARCHAR(100),
    LastName NVARCHAR(100),
    Email NVARCHAR(255) UNIQUE NOT NULL,         -- Unique email of the user
    Role NVARCHAR(50),                           -- User's role (e.g., Manager, Engineer)
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (OrganizationId) REFERENCES Organization(Id),
    FOREIGN KEY (DepartmentId) REFERENCES Department(Id)
);

-- Goal Table (Updated with DueDate)
CREATE TABLE Goal (
    Id INT PRIMARY KEY IDENTITY(1,1),
    OrganizationId INT NOT NULL,                 -- Foreign key to Organization
    Title NVARCHAR(255) NOT NULL,                -- Title of the goal
    DueDate DATETIME NULL,                   -- Due date of the goal (previously Date column)
    InitiatedBy NVARCHAR(255),                   -- Email of the person who initiated the goal
    GoalDescription NVARCHAR(255),               -- Description of the goal
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (OrganizationId) REFERENCES Organization(Id)
);

-- Assignment Table
CREATE TABLE Assignment (
    Id INT PRIMARY KEY IDENTITY(1,1),
    GoalId INT NOT NULL,                         -- Foreign key linking to the Goal
    ParentAssignmentId INT NULL,                 -- Self-referencing foreign key for nested assignments
    QuestionText NVARCHAR(255) NOT NULL,         -- Text of the question
    [Order] INT,                                 -- Display order for the question
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (GoalId) REFERENCES Goal(Id),
    FOREIGN KEY (ParentAssignmentId) REFERENCES Assignment(Id)
);

-- UserResponse Table (Merged from AssignmentUser and Response)
CREATE TABLE UserResponse (
    Id INT PRIMARY KEY IDENTITY(1,1),
    AssignmentId INT NOT NULL,                   -- Foreign key to Assignment
    AssignedTo NVARCHAR(255) NOT NULL,           -- Email of the user assigned to the assignment
    Answer NVARCHAR(MAX),                        -- The response or answer to the question
    Status NVARCHAR(50) DEFAULT 'Assigned',      -- Status of the assignment ('Assigned', 'Draft', 'Final')
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (AssignmentId) REFERENCES Assignment(Id)
);

-- OrganizationSettings Table
CREATE TABLE OrganizationSettings (
    Id INT PRIMARY KEY IDENTITY(1,1),            -- Unique identifier
    OrganizationId INT NOT NULL,                 -- Foreign key linking to Organization
    BusinessSector NVARCHAR(100),                -- Business sector (e.g., Technology, Finance)
    CompanySize NVARCHAR(50),                    -- Company size (e.g., Small, Medium, Large)
    TeamStructure NVARCHAR(MAX),                 -- JSON or comma-separated list of team names
    GeographicFocus NVARCHAR(MAX),               -- JSON or comma-separated list of regions
    HistoricalData NVARCHAR(MAX),                -- Reference to organizational data (e.g., URLs or file paths)
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (OrganizationId) REFERENCES Organization(Id)
);

-- UserSettings Table
CREATE TABLE UserSettings (
    Id INT PRIMARY KEY IDENTITY(1,1),            -- Unique identifier
    UserId INT NOT NULL,                         -- Foreign key linking to User
    Role NVARCHAR(255),                          -- Multi-select role of the user (e.g., CEO, Manager)
    BusinessObjective NVARCHAR(MAX),             -- Multi-select business objectives
    CurrentChallenges NVARCHAR(MAX),             -- Multi-select current challenges
    KPIs NVARCHAR(MAX),                          -- Multi-select KPIs (e.g., Customer Satisfaction)
    TeamMemberRoles NVARCHAR(MAX),               -- Multi-select roles of team members
    PriorityLevel NVARCHAR(50),                  -- Single choice priority level (e.g., Urgent, Normal)
    LevelOfComplexity NVARCHAR(50),              -- Single choice complexity level
    TargetOutcome NVARCHAR(MAX),                 -- Multi-select target outcomes
    CommunicationStyle NVARCHAR(50),             -- Single choice communication style
    GoalTimeframe NVARCHAR(50),                  -- Single choice goal timeframe
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (UserId) REFERENCES [User](Id)
);

-- SubscriptionPlan Table
CREATE TABLE SubscriptionPlan (
    Id INT PRIMARY KEY IDENTITY(1,1),
    PlanName NVARCHAR(100) NOT NULL,             -- Name of the subscription plan
    Price DECIMAL(10, 2) NOT NULL,               -- Price of the subscription plan
    Features NVARCHAR(MAX),                      -- List of features (JSON or text format)
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL                 -- Audit column
);

-- OrganizationSubscription Table
CREATE TABLE OrganizationSubscription (
    Id INT PRIMARY KEY IDENTITY(1,1),
    OrganizationId INT NOT NULL,                 -- Foreign key linking to Organization
    SubscriptionPlanId INT NOT NULL,             -- Foreign key linking to SubscriptionPlan
    StartDate DATE NOT NULL,                     -- Start date of the subscription
    EndDate DATE NOT NULL,                       -- End date of the subscription
    IsActive BIT DEFAULT 1,                      -- Whether the subscription is active or not
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (OrganizationId) REFERENCES Organization(Id),
    FOREIGN KEY (SubscriptionPlanId) REFERENCES SubscriptionPlan(Id)
);

-- Billing Table
CREATE TABLE Billing (
    Id INT PRIMARY KEY IDENTITY(1,1),
    OrganizationId INT NOT NULL,                 -- Foreign key to Organization
    Amount DECIMAL(10, 2) NOT NULL,              -- Billing amount
    BillingPeriodStart DATE,                     -- Start of the billing period
    BillingPeriodEnd DATE,                       -- End of the billing period
    Status NVARCHAR(50),                         -- Billing status (e.g., Paid, Pending)
    PaymentDate DATE,                            -- Date of payment
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (OrganizationId) REFERENCES Organization(Id)
);

-- Feature Table
CREATE TABLE Feature (
    Id INT PRIMARY KEY IDENTITY(1,1),
    FeatureName NVARCHAR(100) NOT NULL,          -- Name of the feature
    Description NVARCHAR(MAX),                   -- Description of the feature
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL                 -- Audit column
);

-- OrganizationFeatureAccess Table
CREATE TABLE OrganizationFeatureAccess (
    Id INT PRIMARY KEY IDENTITY(1,1),
    OrganizationId INT NOT NULL,                 -- Foreign key to Organization
    FeatureId INT NOT NULL,                      -- Foreign key to Feature
    AccessGranted BIT DEFAULT 1,                 -- Whether access is granted or not
    CreatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    UpdatedAt DATETIME DEFAULT GETDATE(),        -- Audit column
    CreatedBy NVARCHAR(255),                     -- Audit column
    UpdatedBy NVARCHAR(255) NULL,                -- Audit column
    FOREIGN KEY (OrganizationId) REFERENCES Organization(Id),
    FOREIGN KEY (FeatureId) REFERENCES Feature(Id)
);

-- AuditLog Table (Updated)
CREATE TABLE AuditLog (
    Id INT PRIMARY KEY IDENTITY(1,1),
    UserId NVARCHAR(255),                        -- User email instead of foreign key
    OrganizationId INT,                          -- Foreign key to Organization
    Action NVARCHAR(255),                        -- Action performed (e.g., Created Assignment, Updated Goal)
    Timestamp DATETIME DEFAULT GETDATE(),        -- Timestamp for the action
    FOREIGN KEY (OrganizationId) REFERENCES Organization(Id)
);
