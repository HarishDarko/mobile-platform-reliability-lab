from __future__ import annotations

import argparse
import socket
import ssl
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_WARNING_DAYS = 30
DEFAULT_CRITICAL_DAYS = 14
DEFAULT_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class CertificateStatus:
    endpoint: str
    expires_at: datetime | None
    days_remaining: int | None
    status: str
    message: str


def read_endpoints(path: Path) -> list[str]:
    endpoints: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith("#"):
            continue
        endpoints.append(candidate)
    return endpoints


def parse_endpoint(endpoint: str) -> tuple[str, int]:
    cleaned = endpoint.removeprefix("https://").split("/", maxsplit=1)[0]
    if not cleaned:
        raise ValueError("endpoint host is empty")

    if ":" in cleaned:
        host, port_text = cleaned.rsplit(":", maxsplit=1)
        return host, int(port_text)

    return cleaned, 443


def get_certificate_expiry(endpoint: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> datetime:
    host, port = parse_endpoint(endpoint)
    context = ssl.create_default_context()

    with socket.create_connection((host, port), timeout=timeout) as tcp_socket:
        with context.wrap_socket(tcp_socket, server_hostname=host) as tls_socket:
            certificate = tls_socket.getpeercert()

    not_after = certificate.get("notAfter")
    if not not_after:
        raise ValueError("certificate does not include notAfter")

    parsed = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
    return parsed.replace(tzinfo=timezone.utc)


def classify_certificate(
    endpoint: str,
    expires_at: datetime,
    now: datetime,
    warning_days: int,
    critical_days: int,
) -> CertificateStatus:
    days_remaining = (expires_at - now).days

    if days_remaining <= critical_days:
        status = "CRITICAL"
    elif days_remaining <= warning_days:
        status = "WARNING"
    else:
        status = "OK"

    return CertificateStatus(
        endpoint=endpoint,
        expires_at=expires_at,
        days_remaining=days_remaining,
        status=status,
        message=f"{status}: {endpoint} certificate expires in {days_remaining} days",
    )


def check_endpoint(
    endpoint: str,
    now: datetime,
    warning_days: int,
    critical_days: int,
    timeout: float,
) -> CertificateStatus:
    try:
        expires_at = get_certificate_expiry(endpoint, timeout=timeout)
    except Exception as exc:
        return CertificateStatus(
            endpoint=endpoint,
            expires_at=None,
            days_remaining=None,
            status="CRITICAL",
            message=f"CRITICAL: {endpoint} certificate check failed: {exc}",
        )

    return classify_certificate(endpoint, expires_at, now, warning_days, critical_days)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check HTTPS certificate expiry for a list of endpoints.")
    parser.add_argument("--endpoints-file", required=True, type=Path)
    parser.add_argument("--warning-days", default=DEFAULT_WARNING_DAYS, type=int)
    parser.add_argument("--critical-days", default=DEFAULT_CRITICAL_DAYS, type=int)
    parser.add_argument("--timeout", default=DEFAULT_TIMEOUT_SECONDS, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    endpoints = read_endpoints(args.endpoints_file)
    now = datetime.now(timezone.utc)

    if not endpoints:
        print(f"CRITICAL: no endpoints found in {args.endpoints_file}")
        return 2

    results = [
        check_endpoint(
            endpoint=endpoint,
            now=now,
            warning_days=args.warning_days,
            critical_days=args.critical_days,
            timeout=args.timeout,
        )
        for endpoint in endpoints
    ]

    for result in results:
        print(result.message)

    if any(result.status == "CRITICAL" for result in results):
        return 2
    if any(result.status == "WARNING" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

