"""FastAPI application entry point."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import engine, Base
from app.middleware.cors import setup_cors
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limit import get_rate_limiter, get_rate_limit_exceeded_handler
from app.api import auth, events, registrations, resources, hackathon_teams
from app.dependencies import get_current_user
from app.utils.errors import create_error_response, AppException

# Security scheme for OpenAPI
security_scheme = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="Cybersecurity Club API",
    description="""
    Secure backend API for Cybersecurity Club website.
    
    ## Features
    
    * **Admin Authentication**: JWT-based authentication with Argon2 password hashing
    * **Event Management**: Create, read, update, and delete events
    * **Registration System**: Public event registration with duplicate prevention
    * **Resource Library**: PDF resource upload, download, and management
    
    ## Authentication
    
    Most endpoints require authentication. Use the `/api/auth/login` endpoint to obtain a JWT token,
    then include it in the Authorization header as: `Bearer <token>`
    
    ## Security
    
    * Rate limiting on sensitive endpoints
    * Input sanitization to prevent XSS attacks
    * File upload validation (PDF only, magic bytes verification)
    * CORS protection
    * Security headers (HSTS, CSP, X-Frame-Options)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Admin authentication endpoints"
        },
        {
            "name": "Events",
            "description": "Event management operations"
        },
        {
            "name": "Registrations",
            "description": "Event registration management"
        },
        {
            "name": "Resources",
            "description": "PDF resource library management"
        },
        {
            "name": "Hackathon Teams",
            "description": "Hackathon team registration"
        },
        {
            "name": "Root",
            "description": "Root and health check endpoints"
        },
        {
            "name": "Health",
            "description": "Health check endpoints"
        }
    ]
)

# Add security scheme to OpenAPI
app.openapi_schema = None  # Force regeneration

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token obtained from /api/auth/login"
        }
    }
    
    # Add security to protected endpoints
    for path, path_item in openapi_schema["paths"].items():
        for method, operation in path_item.items():
            if method in ["post", "put", "delete"] and path not in ["/api/auth/login", "/api/registrations"]:
                if "security" not in operation:
                    operation["security"] = [{"BearerAuth": []}]
            elif method == "get" and path in ["/api/registrations", "/api/registrations/{registration_id}", "/api/registrations/export/csv", "/api/auth/me"]:
                if "security" not in operation:
                    operation["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Initialize rate limiter
limiter = get_rate_limiter()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())

# Add middleware
app.add_middleware(SecurityHeadersMiddleware)
setup_cors(app)

# Create database tables (in production, use Alembic migrations)
if settings.debug:
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(registrations.router)
app.include_router(resources.router)
app.include_router(hackathon_teams.router)

# Error handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            exc.status_code,
            exc.error_code,
            exc.detail,
            exc.details
        ).dict()
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    error_code_map = {
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        413: "PAYLOAD_TOO_LARGE",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR"
    }
    
    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            exc.status_code,
            error_code,
            exc.detail or "An error occurred",
            {}
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors[field] = error["msg"]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            "Validation error",
            {"fields": errors}
        ).dict()
    )


@app.get("/", tags=["Root"])
def root():
    """Root endpoint."""
    return {
        "message": "Cybersecurity Club API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
