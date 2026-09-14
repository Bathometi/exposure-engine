from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from core.rdap import collect_rdap_ip


@pytest.mark.asyncio
async def test_rdap_success_returns_structured_result():
    response = SimpleNamespace(
        status_code=200,
        error=None,
        response_data={
            "handle": "TEST-NET",
            "name": "TEST-NETWORK",
            "startAddress": "192.0.2.0",
            "endAddress": "192.0.2.255",
            "country": "ZZ",
            "type": "DIRECT ALLOCATION",
        },
    )

    collector = SimpleNamespace(
        request=AsyncMock(return_value=response)
    )

    result = await collect_rdap_ip(
        collector,
        "192.0.2.1",
    )

    assert result == {
        "status": "ok",
        "source": "RDAP",
        "ip": "192.0.2.1",
        "handle": "TEST-NET",
        "name": "TEST-NETWORK",
        "start_address": "192.0.2.0",
        "end_address": "192.0.2.255",
        "country": "ZZ",
        "type": "DIRECT ALLOCATION",
        "error": None,
    }

    collector.request.assert_awaited_once_with(
        url="https://rdap.org/ip/192.0.2.1",
        response_type="json",
    )


@pytest.mark.asyncio
async def test_rdap_request_error_means_unavailable():
    response = SimpleNamespace(
        status_code=None,
        error="Request timed out.",
        response_data=None,
    )

    collector = SimpleNamespace(
        request=AsyncMock(return_value=response)
    )

    result = await collect_rdap_ip(
        collector,
        "192.0.2.1",
    )

    assert result == {
        "status": "unavailable",
        "source": "RDAP",
        "ip": "192.0.2.1",
        "handle": None,
        "name": None,
        "start_address": None,
        "end_address": None,
        "country": None,
        "type": None,
        "error": "Request timed out.",
    }


@pytest.mark.asyncio
async def test_rdap_404_means_not_found():
    response = SimpleNamespace(
        status_code=404,
        error=None,
        response_data=None,
    )

    collector = SimpleNamespace(
        request=AsyncMock(return_value=response)
    )

    result = await collect_rdap_ip(
        collector,
        "192.0.2.1",
    )

    assert result == {
        "status": "not_found",
        "source": "RDAP",
        "ip": "192.0.2.1",
        "handle": None,
        "name": None,
        "start_address": None,
        "end_address": None,
        "country": None,
        "type": None,
        "error": None,
    }


@pytest.mark.asyncio
async def test_rdap_http_error_means_unavailable():
    response = SimpleNamespace(
        status_code=503,
        error=None,
        response_data={
            "message": "Service unavailable",
        },
    )

    collector = SimpleNamespace(
        request=AsyncMock(return_value=response)
    )

    result = await collect_rdap_ip(
        collector,
        "192.0.2.1",
    )

    assert result == {
        "status": "unavailable",
        "source": "RDAP",
        "ip": "192.0.2.1",
        "handle": None,
        "name": None,
        "start_address": None,
        "end_address": None,
        "country": None,
        "type": None,
        "error": "HTTP 503",
    }
