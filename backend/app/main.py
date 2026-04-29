import logging
import os
import time
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

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

FAKE_ACCOUNTS = [
    Account(id="demo-chequing-001", name="Everyday Chequing", type="chequing", balance=1240.55),
    Account(id="demo-savings-001", name="High Interest Savings", type="savings", balance=8450.0),
]


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next: Any) -> JSONResponse:
    global REQUEST_COUNT
    REQUEST_COUNT += 1

    request_id = request.headers.get("x-request-id", str(uuid4()))
    start = time.perf_counter()

    logger.info(
        "request_started",
        extra={"request_id": request_id},
    )
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["x-request-id"] = request_id

    logger.info(
        f"request_completed method={request.method} path={request.url.path} "
        f"status={response.status_code} duration_ms={duration_ms}",
        extra={"request_id": request_id},
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
    return "\n".join(
        [
            "# HELP lab_requests_total Total API requests handled by the demo service.",
            "# TYPE lab_requests_total counter",
            f"lab_requests_total {REQUEST_COUNT}",
            "# HELP lab_payments_total Total demo payments accepted.",
            "# TYPE lab_payments_total counter",
            f"lab_payments_total {PAYMENT_COUNT}",
            "",
        ]
    )
