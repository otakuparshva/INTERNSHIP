from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Callable
import time
import redis
from core.config import settings
from core.logging import setup_logger

logger = setup_logger("rate_limit")

# Initialize Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        key_prefix: str = "rate_limit"
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.key_prefix = key_prefix
        self.window_size = 60  # 1 minute window

    def _get_key(self, request: Request) -> str:
        """Generate a unique key for rate limiting"""
        # Use IP address as default identifier
        identifier = request.client.host
        
        # If user is authenticated, use user ID
        if hasattr(request.state, "user"):
            identifier = str(request.state.user.id)
        
        return f"{self.key_prefix}:{identifier}"

    def _check_rate_limit(self, key: str) -> tuple[bool, Optional[float]]:
        """Check if request should be rate limited"""
        current_time = time.time()
        window_start = current_time - self.window_size

        # Get current window data
        pipeline = redis_client.pipeline()
        pipeline.zremrangebyscore(key, 0, window_start)
        pipeline.zadd(key, {str(current_time): current_time})
        pipeline.zcard(key)
        pipeline.expire(key, self.window_size)
        _, _, request_count, _ = pipeline.execute()

        # Check if rate limit is exceeded
        if request_count > self.requests_per_minute + self.burst_size:
            # Calculate time until next window
            oldest_request = float(redis_client.zrange(key, 0, 0, withscores=True)[0][1])
            reset_time = oldest_request + self.window_size - current_time
            return False, reset_time

        return True, None

    async def __call__(self, request: Request, call_next: Callable):
        """Rate limiting middleware"""
        try:
            key = self._get_key(request)
            allowed, reset_time = self._check_rate_limit(key)

            if not allowed:
                logger.warning(
                    "Rate limit exceeded",
                    extra={
                        "ip": request.client.host,
                        "path": request.url.path,
                        "reset_time": reset_time
                    }
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many requests",
                        "retry_after": int(reset_time) if reset_time else None
                    }
                )

            response = await call_next(request)
            return response

        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {str(e)}")
            # On Redis error, allow the request but log the error
            return await call_next(request)

        except Exception as e:
            logger.error(f"Rate limiter error: {str(e)}")
            # On other errors, allow the request but log the error
            return await call_next(request)

# Create rate limiter instances for different endpoints
default_limiter = RateLimiter(
    requests_per_minute=60,
    burst_size=10,
    key_prefix="default"
)

auth_limiter = RateLimiter(
    requests_per_minute=30,
    burst_size=5,
    key_prefix="auth"
)

admin_limiter = RateLimiter(
    requests_per_minute=120,
    burst_size=20,
    key_prefix="admin"
)

api_limiter = RateLimiter(
    requests_per_minute=100,
    burst_size=15,
    key_prefix="api"
) 