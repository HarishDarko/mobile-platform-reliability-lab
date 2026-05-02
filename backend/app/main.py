import logging
import os
import time
from collections import defaultdict
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response

from app.logging_config import configure_logging
from app.models import Account, PaymentRequest, PaymentResponse

configure_logging()
logger = logging.getLogger("mobile-platform-lab")

app = FastAPI(
    title="Mobile Platform Reliability Lab API",
    description="Fake mobile banking style API for DevOps and SRE practice.",
    version="0.1.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_COUNT = 0
PAYMENT_COUNT = 0
ERROR_COUNT = 0
REQUESTS_BY_ROUTE: dict[tuple[str, str, int], int] = defaultdict(int)
REQUESTS_BY_CLIENT_CONTEXT: dict[tuple[str, str, str], int] = defaultdict(int)
REQUEST_DURATION_SECONDS_SUM_BY_ROUTE: dict[tuple[str, str], float] = defaultdict(float)
REQUEST_DURATION_SECONDS_COUNT_BY_ROUTE: dict[tuple[str, str], int] = defaultdict(int)
REQUEST_DURATION_SECONDS_MAX_BY_ROUTE: dict[tuple[str, str], float] = defaultdict(float)

FAKE_ACCOUNTS = [
    Account(id="demo-chequing-001", name="Everyday Chequing", type="chequing", balance=1240.55),
    Account(id="demo-savings-001", name="High Interest Savings", type="savings", balance=8450.0),
]


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next: Any) -> Response:
    global ERROR_COUNT, REQUEST_COUNT
    REQUEST_COUNT += 1

    request_id = request.headers.get("x-request-id", str(uuid4()))
    start = time.perf_counter()
    method = request.method
    path = request.url.path
    client_platform = request.headers.get("x-client-platform", "unknown")
    app_version = request.headers.get("x-app-version", "unknown")
    app_environment = request.headers.get("x-app-environment", "unknown")

    logger.info(
        "request_started",
        extra={
            "event": "request_started",
            "request_id": request_id,
            "method": method,
            "path": path,
            "client": request.client.host if request.client else None,
            "client_platform": client_platform,
            "app_version": app_version,
            "app_environment": app_environment,
        },
    )
    response = await call_next(request)
    duration_seconds = time.perf_counter() - start
    duration_ms = round(duration_seconds * 1000, 2)
    status_code = response.status_code
    response.headers["x-request-id"] = request_id

    REQUESTS_BY_ROUTE[(method, path, status_code)] += 1
    REQUESTS_BY_CLIENT_CONTEXT[(client_platform, app_version, app_environment)] += 1
    REQUEST_DURATION_SECONDS_SUM_BY_ROUTE[(method, path)] += duration_seconds
    REQUEST_DURATION_SECONDS_COUNT_BY_ROUTE[(method, path)] += 1
    REQUEST_DURATION_SECONDS_MAX_BY_ROUTE[(method, path)] = max(
        REQUEST_DURATION_SECONDS_MAX_BY_ROUTE[(method, path)],
        duration_seconds,
    )
    if status_code >= 500:
        ERROR_COUNT += 1

    logger.info(
        "request_completed",
        extra={
            "event": "request_completed",
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "client_platform": client_platform,
            "app_version": app_version,
            "app_environment": app_environment,
        },
    )
    return response


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "mobile-platform-reliability-api",
        "runtime_secret_configured": bool(os.getenv("DEMO_RUNTIME_SECRET")),
    }


@app.get("/accounts", response_model=list[Account])
def get_accounts() -> list[Account]:
    return FAKE_ACCOUNTS


@app.post("/payments", response_model=PaymentResponse)
def create_payment(payment: PaymentRequest) -> PaymentResponse:
    global PAYMENT_COUNT

    account_ids = {account.id for account in FAKE_ACCOUNTS}
    if payment.from_account_id not in account_ids:
        raise HTTPException(status_code=404, detail="Source account not found")

    PAYMENT_COUNT += 1
    return PaymentResponse(
        payment_id=f"demo-payment-{PAYMENT_COUNT:04d}",
        status="accepted",
        message=f"Demo payment to {payment.to_payee} accepted for processing.",
    )


@app.get("/slow")
def slow_response() -> dict[str, str]:
    time.sleep(2)
    return {"status": "slow", "message": "Simulated latency for troubleshooting practice"}


@app.get("/error")
def error_response() -> None:
    raise HTTPException(status_code=500, detail="Simulated backend failure")


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    lines = [
        "# HELP lab_requests_total Total API requests handled by the demo service.",
        "# TYPE lab_requests_total counter",
        f"lab_requests_total {REQUEST_COUNT}",
        "# HELP lab_payments_total Total demo payments accepted.",
        "# TYPE lab_payments_total counter",
        f"lab_payments_total {PAYMENT_COUNT}",
        "# HELP lab_errors_total Total API responses with HTTP status code 500 or higher.",
        "# TYPE lab_errors_total counter",
        f"lab_errors_total {ERROR_COUNT}",
        "# HELP lab_http_requests_total API requests by method, path, and status code.",
        "# TYPE lab_http_requests_total counter",
    ]

    for (method, path, status_code), count in sorted(REQUESTS_BY_ROUTE.items()):
        lines.append(
            "lab_http_requests_total"
            f'{{method="{method}",path="{path}",status_code="{status_code}"}} {count}'
        )

    lines.extend(
        [
            "# HELP lab_mobile_client_requests_total API requests by mobile client context.",
            "# TYPE lab_mobile_client_requests_total counter",
        ]
    )
    for (client_platform, app_version, app_environment), count in sorted(REQUESTS_BY_CLIENT_CONTEXT.items()):
        lines.append(
            "lab_mobile_client_requests_total"
            f'{{client_platform="{client_platform}",app_version="{app_version}",'
            f'app_environment="{app_environment}"}} {count}'
        )

    lines.extend(
        [
            "# HELP lab_http_request_duration_seconds_sum Total request duration by method and path.",
            "# TYPE lab_http_request_duration_seconds_sum counter",
        ]
    )
    for (method, path), duration_sum in sorted(REQUEST_DURATION_SECONDS_SUM_BY_ROUTE.items()):
        lines.append(
            "lab_http_request_duration_seconds_sum"
            f'{{method="{method}",path="{path}"}} {duration_sum:.6f}'
        )

    lines.extend(
        [
            "# HELP lab_http_request_duration_seconds_count Request duration sample count by method and path.",
            "# TYPE lab_http_request_duration_seconds_count counter",
        ]
    )
    for (method, path), count in sorted(REQUEST_DURATION_SECONDS_COUNT_BY_ROUTE.items()):
        lines.append(
            "lab_http_request_duration_seconds_count"
            f'{{method="{method}",path="{path}"}} {count}'
        )

    lines.extend(
        [
            "# HELP lab_http_request_duration_seconds_max Maximum observed request duration by method and path.",
            "# TYPE lab_http_request_duration_seconds_max gauge",
        ]
    )
    for (method, path), duration_max in sorted(REQUEST_DURATION_SECONDS_MAX_BY_ROUTE.items()):
        lines.append(
            "lab_http_request_duration_seconds_max"
            f'{{method="{method}",path="{path}"}} {duration_max:.6f}'
        )

    lines.append("")
    return "\n".join(lines)
