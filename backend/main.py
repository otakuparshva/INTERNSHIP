from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from .core.config import settings
from .core.logging import setup_logger, log_request
from .core.rate_limit import default_limiter, auth_limiter, admin_limiter, api_limiter
from .routers import auth, admin, jobs, candidates, recruiters
import time
import traceback

# Setup logging
logger = setup_logger("main")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI Recruitment System API",
        version="1.0.0",
        description="""
        # AI Recruitment System API Documentation
        
        This API provides endpoints for managing the recruitment process, including:
        
        * User authentication and authorization
        * Job posting and management
        * Candidate applications and tracking
        * Recruiter operations
        * Admin dashboard functionality
        
        ## Authentication
        
        All endpoints except `/api/auth/register` and `/api/auth/login` require authentication.
        Include the JWT token in the Authorization header:
        
        ```
        Authorization: Bearer <your_token>
        ```
        
        ## Rate Limiting
        
        The API implements rate limiting to prevent abuse:
        * Auth endpoints: 5 requests per minute
        * Admin endpoints: 10 requests per minute
        * Other endpoints: 20 requests per minute
        """,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

app.openapi = custom_openapi

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Add rate limiting middleware
app.middleware("http")(default_limiter)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.response_time = process_time
        log_request(request, response)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        log_request(request, error=e)
        raise

# Add error handling middleware
@app.middleware("http")
async def error_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(
            "Unhandled exception",
            extra={
                "error": str(e),
                "stack_trace": traceback.format_exc(),
                "path": request.url.path,
                "method": request.method,
            }
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

# Include routers with rate limiting
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["auth"],
    dependencies=[auth_limiter]
)

app.include_router(
    admin.router,
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[admin_limiter]
)

app.include_router(
    jobs.router,
    prefix="/api/jobs",
    tags=["jobs"],
    dependencies=[api_limiter]
)

app.include_router(
    candidates.router,
    prefix="/api/candidates",
    tags=["candidates"],
    dependencies=[api_limiter]
)

app.include_router(
    recruiters.router,
    prefix="/api/recruiters",
    tags=["recruiters"],
    dependencies=[api_limiter]
)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Recruitment System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 