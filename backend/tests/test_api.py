from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["runtime_secret_configured"] is False
    assert "x-request-id" in response.headers


def test_accounts_returns_fake_demo_accounts() -> None:
    response = client.get("/accounts")

    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) == 2
    assert accounts[0]["currency"] == "CAD"


def test_payment_accepts_known_account() -> None:
    response = client.post(
        "/payments",
        json={
            "from_account_id": "demo-chequing-001",
            "to_payee": "Demo Utility",
            "amount": 25.5,
            "currency": "CAD",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["payment_id"].startswith("demo-payment-")


def test_payment_rejects_unknown_account() -> None:
    response = client.post(
        "/payments",
        json={
            "from_account_id": "missing-account",
            "to_payee": "Demo Utility",
            "amount": 25.5,
            "currency": "CAD",
        },
    )

    assert response.status_code == 404


def test_error_endpoint_simulates_failure() -> None:
    response = client.get("/error")

    assert response.status_code == 500
    assert response.json()["detail"] == "Simulated backend failure"


def test_metrics_returns_prometheus_style_text() -> None:
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "lab_requests_total" in response.text
    assert "lab_payments_total" in response.text
