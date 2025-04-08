from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info
from prometheus_client import Counter, Histogram
import time

# Custom metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

def setup_monitoring(app):
    # Add default metrics
    Instrumentator().instrument(app).expose(app)
    
    # Add custom metrics
    @app.middleware("http")
    async def monitor_requests(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
    
    # Add business metrics
    applications_total = Counter(
        "applications_total",
        "Total number of job applications",
        ["status"]
    )
    
    jobs_posted_total = Counter(
        "jobs_posted_total",
        "Total number of jobs posted",
        ["department"]
    )
    
    return {
        "applications_total": applications_total,
        "jobs_posted_total": jobs_posted_total
    } 