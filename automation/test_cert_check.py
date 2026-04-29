from datetime import datetime, timedelta, timezone
from pathlib import Path

from cert_check import classify_certificate, parse_endpoint, read_endpoints


def test_read_endpoints_ignores_comments_and_blank_lines(tmp_path: Path) -> None:
    endpoints_file = tmp_path / "endpoints.txt"
    endpoints_file.write_text(
        "\n# comment\nhttps://api.example.com\n\nhttps://login.example.com\n",
        encoding="utf-8",
    )

    assert read_endpoints(endpoints_file) == [
        "https://api.example.com",
        "https://login.example.com",
    ]


def test_parse_endpoint_defaults_to_https_port() -> None:
    assert parse_endpoint("https://api.example.com/health") == ("api.example.com", 443)


def test_parse_endpoint_supports_custom_port() -> None:
    assert parse_endpoint("https://api.example.com:8443/health") == ("api.example.com", 8443)


def test_classify_certificate_ok() -> None:
    now = datetime(2026, 4, 28, tzinfo=timezone.utc)
    expires_at = now + timedelta(days=60)

    result = classify_certificate("https://api.example.com", expires_at, now, 30, 14)

    assert result.status == "OK"
    assert result.days_remaining == 60


def test_classify_certificate_warning() -> None:
    now = datetime(2026, 4, 28, tzinfo=timezone.utc)
    expires_at = now + timedelta(days=20)

    result = classify_certificate("https://api.example.com", expires_at, now, 30, 14)

    assert result.status == "WARNING"
    assert result.days_remaining == 20


def test_classify_certificate_critical() -> None:
    now = datetime(2026, 4, 28, tzinfo=timezone.utc)
    expires_at = now + timedelta(days=7)

    result = classify_certificate("https://api.example.com", expires_at, now, 30, 14)

    assert result.status == "CRITICAL"
    assert result.days_remaining == 7

