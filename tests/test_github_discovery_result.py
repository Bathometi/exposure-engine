from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from core.github_mentions import discover_github_mentions


@pytest.mark.asyncio
async def test_github_discovery_preserves_http_error(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    response = SimpleNamespace(
        error=None,
        status_code=503,
        response_data=None,
    )

    collector = SimpleNamespace(
        request=AsyncMock(return_value=response)
    )

    result = await discover_github_mentions(
        collector,
        "TEST_PHONE",
    )

    assert result["status"] == "unavailable"
    assert result["mentions"] == []
    assert result["error"] is not None
