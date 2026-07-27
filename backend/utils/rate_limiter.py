import time
from collections import defaultdict
from threading import Lock
from fastapi import Request, HTTPException, status

class RateLimiter:
    """
    Sliding window in-memory rate limiter per IP address for FastAPI endpoints.
    """
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()

    def _cleanup_expired(self, ip: str, now: float):
        cutoff = now - self.window_seconds
        self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]
        if not self.requests[ip]:
            del self.requests[ip]

    def check_rate_limit(self, request: Request):
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        with self.lock:
            self._cleanup_expired(client_ip, now)
            timestamps = self.requests[client_ip]

            if len(timestamps) >= self.max_requests:
                oldest = timestamps[0]
                retry_after = int(self.window_seconds - (now - oldest)) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many attempts. Please try again in {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)}
                )

            self.requests[client_ip].append(now)

# Pre-configured instance: 5 attempts per 60 seconds for sensitive auth endpoints
auth_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)

def limit_auth_requests(request: Request):
    auth_rate_limiter.check_rate_limit(request)
