from fastapi import FastAPI, status
from db.models import Base
from api.routes import test, analysis, client, organization, department, goal, assignment, response, organization_settings, user_settings, user, subscription_plan, organization_subscription, billing, feature, organization_feature_access, audit_log
from db.database import engine
import uvicorn
import os
import logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Completely disable CORS by allowing all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allow all origins
    allow_credentials=True,        # Allow credentials (cookies, auth headers)
    allow_methods=["*"],           # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],           # Allow all headers
)

logging.info("CORS is completely disabled. All origins, methods, and headers are allowed.")

# Database setup
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(client.router, prefix="/api/v1", tags=["Client"])
app.include_router(organization.router, prefix="/api/v1", tags=["Organization"])
app.include_router(department.router, prefix="/api/v1", tags=["Department"])
app.include_router(goal.router, prefix="/api/v1", tags=["Goal"])
app.include_router(assignment.router, prefix="/api/v1", tags=["Assignment"])
app.include_router(response.router, prefix="/api/v1", tags=["Response"])
app.include_router(organization_settings.router, prefix="/api/v1", tags=["OrganizationSettings"])
app.include_router(user.router, prefix="/api/v1", tags=["User"])
app.include_router(user_settings.router, prefix="/api/v1", tags=["UserSettings"])
app.include_router(subscription_plan.router, prefix="/api/v1", tags=["SubscriptionPlan"])
app.include_router(organization_subscription.router, prefix="/api/v1", tags=["OrganizationSubscription"])
app.include_router(billing.router, prefix="/api/v1", tags=["Billing"])
app.include_router(feature.router, prefix="/api/v1", tags=["Feature"])
app.include_router(organization_feature_access.router, prefix="/api/v1", tags=["OrganizationFeatureAccess"])
app.include_router(audit_log.router, prefix="/api/v1", tags=["AuditLog"])

# Health check endpoints
@app.get("/", status_code=status.HTTP_200_OK, tags=["Health"])
def root():
    return {"message": "API is running"}

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), reload=True)
