import logging
import os
import time
from collections import defaultdict, deque
from typing import Any
from uuid import uuid4

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
DEMO_API_KEY = os.getenv("DEMO_API_KEY", "demo-mobile-key")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))

logger = logging.getLogger("gateway")
logging.basicConfig(level=logging.INFO, format="%(message)s")

app = FastAPI(
    title="Mobile API Gateway Simulator",
    description="Small API gateway style layer that demonstrates Apigee concepts locally.",
    version="0.1.0",
)

request_windows: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Any) -> JSONResponse:
    request_id = request.headers.get("x-request-id", str(uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["x-request-id"] = request_id
    logger.info(
        {
            "event": "gateway_request_completed",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }
    )
    return response


def enforce_api_key(x_api_key: str | None) -> None:
    if x_api_key != DEMO_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def enforce_rate_limit(client_id: str) -> None:
    now = time.time()
    window = request_windows[client_id]

    while window and now - window[0] > 60:
        window.popleft()

    if len(window) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    window.append(now)


async def forward_json(
    method: str,
    path: str,
    request_id: str,
    json_body: dict[str, Any] | None = None,
) -> JSONResponse:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.request(
                method,
                f"{BACKEND_BASE_URL}{path}",
                json=json_body,
                headers={"x-request-id": request_id},
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Backend target unavailable: {exc}") from exc

    return JSONResponse(
        status_code=response.status_code,
        content=response.json(),
        headers={"x-request-id": request_id},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "mobile-api-gateway-simulator"}


@app.get("/mobile/v1/accounts")
async def mobile_accounts(
    request: Request,
    x_api_key: str | None = Header(default=None),
    x_client_id: str = Header(default="anonymous"),
) -> JSONResponse:
    enforce_api_key(x_api_key)
    enforce_rate_limit(x_client_id)
    request_id = request.headers.get("x-request-id", str(uuid4()))
    return await forward_json("GET", "/accounts", request_id)


@app.post("/mobile/v1/payments")
async def mobile_payments(
    request: Request,
    x_api_key: str | None = Header(default=None),
    x_client_id: str = Header(default="anonymous"),
) -> JSONResponse:
    enforce_api_key(x_api_key)
    enforce_rate_limit(x_client_id)
    request_id = request.headers.get("x-request-id", str(uuid4()))
    body = await request.json()
    return await forward_json("POST", "/payments", request_id, json_body=body)

