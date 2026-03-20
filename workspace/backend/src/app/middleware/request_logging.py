"""
Request / response logging middleware.
Logs method, path, status code, and duration for every request.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured per-request logging with a unique request ID."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start = time.perf_counter()

        logger.info(
            "→ %s %s  [req=%s]",
            request.method,
            request.url.path,
            request_id,
        )

        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            elapsed = (time.perf_counter() - start) * 1000
            logger.error(
                "✗ %s %s  [req=%s]  %.1fms  ERROR: %s",
                request.method,
                request.url.path,
                request_id,
                elapsed,
                exc,
            )
            raise

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "← %s %s  [req=%s]  %d  %.1fms",
            request.method,
            request.url.path,
            request_id,
            response.status_code,
            elapsed,
        )

        response.headers["X-Request-ID"] = request_id
        return response
