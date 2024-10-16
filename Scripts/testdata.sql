-- Insert into Client
INSERT INTO Client (Name, ContactEmail, ContactPhone, Address, CreatedBy) 
VALUES ('Acme Corp', 'contact@acme.com', '123-456-7890', '123 Main St', 'admin@acme.com');

-- Insert into Organization
INSERT INTO Organization (ClientId, Name, Address, ContactEmail, ContactPhone, CreatedBy)
VALUES (1, 'Acme Corp Headquarters', '456 Business Rd', 'hq@acme.com', '987-654-3210', 'admin@acme.com');

-- Insert into Department
INSERT INTO Department (OrganizationId, Name, ManagerName, CreatedBy)
VALUES (1, 'Sales Department', 'John Doe', 'admin@acme.com');

-- Insert into User
INSERT INTO [User] (OrganizationId, DepartmentId, FirstName, LastName, Email, Role, CreatedBy)
VALUES (1, 1, 'Alice', 'Smith', 'alice@acme.com', 'Sales Manager', 'admin@acme.com');

INSERT INTO [User] (OrganizationId, DepartmentId, FirstName, LastName, Email, Role, CreatedBy)
VALUES (1, 1, 'Bob', 'Johnson', 'bob@acme.com', 'Sales Executive', 'admin@acme.com');

-- Insert into Goal
INSERT INTO Goal (OrganizationId, Title, DueDate, InitiatedBy, GoalDescription, CreatedBy)
VALUES (1, 'Increase Sales for Q4', '2024-12-31', 'alice@acme.com', 'Increase overall sales by 10%', 'admin@acme.com');

-- Insert into Assignment (parent and child assignments for hierarchy)
INSERT INTO Assignment (GoalId, QuestionText, [Order], CreatedBy)
VALUES (1, 'What is the sales strategy for Q4?', 1, 'alice@acme.com');

-- Child assignment (linked to the parent above)
INSERT INTO Assignment (GoalId, ParentAssignmentId, QuestionText, [Order], CreatedBy)
VALUES (1, 1, 'How will we increase product X sales?', 1, 'alice@acme.com');

-- Another child assignment (linked to the parent above)
INSERT INTO Assignment (GoalId, ParentAssignmentId, QuestionText, [Order], CreatedBy)
VALUES (1, 1, 'What is the marketing budget for Q4?', 2, 'alice@acme.com');

-- Second parent assignment
INSERT INTO Assignment (GoalId, QuestionText, [Order], CreatedBy)
VALUES (1, 'What are the projected revenue figures for Q4?', 2, 'bob@acme.com');

-- Insert into UserResponse (Assignment, user responses with status)
INSERT INTO UserResponse (AssignmentId, AssignedTo, Answer, Status, CreatedBy)
VALUES (1, 'bob@acme.com', 'Strategy is being finalized', 'Draft', 'alice@acme.com');

INSERT INTO UserResponse (AssignmentId, AssignedTo, Answer, Status, CreatedBy)
VALUES (2, 'alice@acme.com', 'Focus on new customer acquisition', 'Final', 'bob@acme.com');

INSERT INTO UserResponse (AssignmentId, AssignedTo, Answer, Status, CreatedBy)
VALUES (3, 'alice@acme.com', 'Budget is under discussion', 'Assigned', 'bob@acme.com');

INSERT INTO UserResponse (AssignmentId, AssignedTo, Answer, Status, CreatedBy)
VALUES (4, 'bob@acme.com', NULL, 'Assigned', 'alice@acme.com');

-- Insert into OrganizationSettings
INSERT INTO OrganizationSettings (OrganizationId, BusinessSector, CompanySize, TeamStructure, GeographicFocus, CreatedBy)
VALUES (1, 'Technology', 'Medium', 'Sales, Marketing, HR', 'North America', 'admin@acme.com');

-- Insert into UserSettings
INSERT INTO UserSettings (UserId, Role, BusinessObjective, CurrentChallenges, KPIs, TeamMemberRoles, PriorityLevel, LevelOfComplexity, TargetOutcome, CommunicationStyle, GoalTimeframe, CreatedBy)
VALUES (1, 'Sales Manager', 'Increase revenue', 'Market competition', 'Revenue, Customer Satisfaction', 'Sales Team', 'Urgent', 'High', 'Achieve 10% sales increase', 'Direct', 'Quarterly', 'admin@acme.com');

-- Insert into SubscriptionPlan
INSERT INTO SubscriptionPlan (PlanName, Price, Features, CreatedBy)
VALUES ('Premium Plan', 99.99, 'Full Access to all features', 'admin@acme.com');

-- Insert into OrganizationSubscription
INSERT INTO OrganizationSubscription (OrganizationId, SubscriptionPlanId, StartDate, EndDate, IsActive, CreatedBy)
VALUES (1, 1, '2024-01-01', '2024-12-31', 1, 'admin@acme.com');

-- Insert into Billing
INSERT INTO Billing (OrganizationId, Amount, BillingPeriodStart, BillingPeriodEnd, Status, PaymentDate, CreatedBy)
VALUES (1, 99.99, '2024-01-01', '2024-01-31', 'Paid', '2024-02-01', 'admin@acme.com');

-- Insert into Feature
INSERT INTO Feature (FeatureName, Description, CreatedBy)
VALUES ('Advanced Reporting', 'Access to advanced sales and revenue reports', 'admin@acme.com');

-- Insert into OrganizationFeatureAccess
INSERT INTO OrganizationFeatureAccess (OrganizationId, FeatureId, AccessGranted, CreatedBy)
VALUES (1, 1, 1, 'admin@acme.com');

-- Insert into AuditLog
INSERT INTO AuditLog (UserId, OrganizationId, Action, Timestamp)
VALUES ('alice@acme.com', 1, 'Created new sales strategy assignment', GETDATE());

INSERT INTO AuditLog (UserId, OrganizationId, Action, Timestamp)
VALUES ('bob@acme.com', 1, 'Updated the marketing budget response', GETDATE());
