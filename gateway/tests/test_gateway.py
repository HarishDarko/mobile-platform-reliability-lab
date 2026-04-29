from fastapi.testclient import TestClient

from app.main import DEMO_API_KEY, app, enforce_rate_limit, request_windows


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_accounts_requires_api_key() -> None:
    response = client.get("/mobile/v1/accounts")

    assert response.status_code == 401


def test_rate_limit_allows_requests_under_limit() -> None:
    request_windows.clear()

    enforce_rate_limit("test-client")

    assert len(request_windows["test-client"]) == 1


def test_accounts_with_api_key_reaches_gateway_policy_before_backend() -> None:
    response = client.get(
        "/mobile/v1/accounts",
        headers={
            "x-api-key": DEMO_API_KEY,
            "x-client-id": "unit-test-client",
        },
    )

    # The local backend may not be running during this unit test, so 502 is acceptable here.
    assert response.status_code in {200, 502}

