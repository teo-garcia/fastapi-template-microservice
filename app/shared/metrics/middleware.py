import time

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

UNKNOWN_ROUTE = "__unknown__"

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "route"],
)


def _route_label(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else UNKNOWN_ROUTE


class MetricsMiddleware(BaseHTTPMiddleware):
    """Records Prometheus metrics for every HTTP request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        route = _route_label(request)
        REQUEST_COUNT.labels(method=request.method, route=route, status=str(response.status_code)).inc()
        REQUEST_DURATION.labels(method=request.method, route=route).observe(duration)

        return response
