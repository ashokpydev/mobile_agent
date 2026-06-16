import time
from collections import defaultdict, deque
from collections.abc import Deque

from fastapi import Header, HTTPException, status

from app.core.config import settings


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, Deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.monotonic()
        window_start = now - 60
        bucket = self._requests[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
            )
        bucket.append(now)


rate_limiter = SlidingWindowRateLimiter()


async def enforce_rate_limit(
    x_device_id: str | None = Header(default=None),
    x_forwarded_for: str | None = Header(default=None),
) -> None:
    key = x_device_id or x_forwarded_for or "anonymous"
    rate_limiter.check(key)

