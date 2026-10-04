"""
Lightweight in-memory rate limiter for API endpoints (e.g. real-time predictions).
"""
import time
import logging
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request, status

logger = logging.getLogger("modelforge.rate_limit")


class InMemoryRateLimiter:
    def __init__(self, requests_per_minute: int = 120):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60.0
        # Maps client identifier -> list of request timestamps
        self._history: Dict[str, List[float]] = defaultdict(list)

    def check(self, identifier: str) -> None:
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old timestamps
        timestamps = [ts for ts in self._history[identifier] if ts > cutoff]
        self._history[identifier] = timestamps

        if len(timestamps) >= self.requests_per_minute:
            retry_after = int(self.window_seconds - (now - timestamps[0])) + 1
            logger.warning("Rate limit exceeded for %s: %d reqs/min", identifier, len(timestamps))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
                headers={"Retry-After": str(max(1, retry_after))},
            )

        self._history[identifier].append(now)


# Default singleton instance for prediction endpoints
prediction_rate_limiter = InMemoryRateLimiter(requests_per_minute=120)


def rate_limit_predictions(request: Request) -> None:
    """
    FastAPI dependency to rate-limit real-time prediction requests.
    """
    # Prefer client host, fallback to 'anonymous'
    client_ip = request.client.host if request.client else "unknown"
    auth_header = request.headers.get("Authorization", "")
    identifier = auth_header if auth_header else client_ip
    prediction_rate_limiter.check(identifier)
