from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from core.internetdb import collect_internetdb_host


@pytest.mark.asyncio
async def test_internetdb_success_returns_structured_result():
    response = SimpleNamespace(
        status_code=200,
        error=None,
        response_data={
            "ip": "TEST_IP",
            "ports": [53, 443],
            "hostnames": ["example.test"],
            "cpes": [],
            "tags": [],
            "vulns": [],
        },
    )

    collector = SimpleNamespace(
        request=AsyncMock(return_value=response)
    )

    result = await collect_internetdb_host(
        collector,
        "TEST_IP",
    )

    assert result == {
        "status": "ok",
        "source": "Shodan InternetDB",
        "ip": "TEST_IP",
        "ports": [53, 443],
        "hostnames": ["example.test"],
        "cpes": [],
        "tags": [],
        "vulns": [],
        "error": None,
    }

    collector.request.assert_awaited_once_with(
        url="https://internetdb.shodan.io/TEST_IP",
        response_type="json",
    )


@pytest.mark.asyncio
async def test_internetdb_404_means_not_indexed():
    response = SimpleNamespace(
        status_code=404,
        error=None,
        response_data=None,
    )

    collector = SimpleNamespace(
        request=AsyncMock(return_value=response)
    )

    result = await collect_internetdb_host(
        collector,
        "TEST_IP",
    )

    assert result == {
        "status": "not_indexed",
        "source": "Shodan InternetDB",
        "ip": "TEST_IP",
        "ports": [],
        "hostnames": [],
        "cpes": [],
        "tags": [],
        "vulns": [],
        "error": None,
    }


@pytest.mark.asyncio
async def test_internetdb_request_error_means_unavailable():
    response = SimpleNamespace(
        status_code=None,
        error="Request timed out.",
        response_data=None,
    )

    collector = SimpleNamespace(
        request=AsyncMock(return_value=response)
    )

    result = await collect_internetdb_host(
        collector,
        "TEST_IP",
    )

    assert result == {
        "status": "unavailable",
        "source": "Shodan InternetDB",
        "ip": "TEST_IP",
        "ports": [],
        "hostnames": [],
        "cpes": [],
        "tags": [],
        "vulns": [],
        "error": "Request timed out.",
    }


@pytest.mark.asyncio
async def test_internetdb_http_error_means_unavailable():
    response = SimpleNamespace(
        status_code=403,
        error=None,
        response_data={
            "message": "Forbidden",
        },
    )

    collector = SimpleNamespace(
        request=AsyncMock(return_value=response)
    )

    result = await collect_internetdb_host(
        collector,
        "TEST_IP",
    )

    assert result == {
        "status": "unavailable",
        "source": "Shodan InternetDB",
        "ip": "TEST_IP",
        "ports": [],
        "hostnames": [],
        "cpes": [],
        "tags": [],
        "vulns": [],
        "error": "HTTP 403",
    }
