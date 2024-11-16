from fastapi import FastAPI, status
from db.models import Base
from api.routes import test, client, organization, department, goal, assignment,  response, organization_settings, user_settings, user, subscription_plan, organization_subscription, billing, feature, organization_feature_access, audit_log
import uvicorn
from db.database import engine
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
# from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry import trace
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = FastAPI()

# Setup tracing and Azure Application Insights (commented out for now)
# trace.set_tracer_provider(TracerProvider())
# span_processor = BatchSpanProcessor(
#     AzureMonitorTraceExporter.from_connection_string(
#         APPLICATIONINSIGHTS_CONNECTION_STRING
#     )
# )
# trace.get_tracer_provider().add_span_processor(span_processor)
# FastAPIInstrumentor.instrument_app(app=app, tracer_provider=trace.get_tracer_provider())

# Define allowed origins (e.g., React frontend domain)
origins = [
    "http://localhost:3001",  # Allow requests from your React app running on this port
    "http://localhost:3000",  # If you might use another port for React
  
    # Add any other frontend domains you want to allow
]

# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of allowed origins
    allow_credentials=True,         # Whether credentials are allowed
    allow_methods=["*"],            # Allowed HTTP methods (GET, POST, etc.)
    allow_headers=["*"],            # Allowed HTTP headers
)

print("CORS middleware configured with origins: %s", origins)
# Uncomment for debugging setup if needed
# if os.getenv("DEBUG", "false").lower() == "true":
#     debugpy.listen(("0.0.0.0", 5678))
#     debugpy.wait_for_client()

# Create the necessary database tables
Base.metadata.create_all(bind=engine)

# Include the routers for all the different entities
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
@app.get("/",
         status_code=status.HTTP_200_OK,
         summary="Azure health check",
         description="Used to avoid 404 errors on Azure app insights due to Always On",
         tags=["Health"])
def root():
    return {"message": "API is running"}


@app.get('/api/health', tags=["Health"])
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8082, reload=True)
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logging.error(f"Error processing request: {exc}")
    return {"message": "An error occurred", "details": str(exc)}

