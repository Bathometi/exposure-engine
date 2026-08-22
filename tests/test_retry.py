import pytest

import core.collector as collector_module

from core.collector import HTTPCollector
from core.schema import EntityType, StatusEnum
from config.platforms import PLATFORMS


@pytest.mark.asyncio
async def test_retry_uses_exponential_backoff(monkeypatch):
    statuses = [503, 503, 503, 200]

    sleep_calls = []
    state = {
        "requests": 0,
    }

    class FakeResponse:
        def __init__(self, status):
            self.status = status

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def json(self):
            return {
                "name": "Test User",
                "username": "testuser",
            }

        async def text(self):
            return ""

    class FakeClientSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url, headers=None, params=None, allow_redirects=True):
            state["requests"] += 1
            status = statuses.pop(0)

            return FakeResponse(status)

    async def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(
        collector_module.aiohttp,
        "ClientSession",
        FakeClientSession,
    )

    monkeypatch.setattr(
        collector_module.asyncio,
        "sleep",
        fake_sleep,
    )

    collector = HTTPCollector(
        timeout_seconds=5,
        max_retries=3,
    )

    evidence = await collector.check_platform(
        entity_type=EntityType.USERNAME,
        raw_value="testuser",
        normalized_value="testuser",
        source_name="GitHub",
        platform_config=PLATFORMS["GitHub"],
    )

    assert evidence.status == StatusEnum.FOUND
    assert state["requests"] == 4
    assert sleep_calls == [2, 4, 8]


@pytest.mark.asyncio
async def test_exhausted_server_retries_return_error(monkeypatch):
    statuses = [503, 503, 503, 503]

    sleep_calls = []
    state = {
        "requests": 0,
    }

    class FakeResponse:
        def __init__(self, status):
            self.status = status

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def json(self):
            return None

        async def text(self):
            return ""

    class FakeClientSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url, headers=None, params=None, allow_redirects=True):
            state["requests"] += 1
            status = statuses.pop(0)

            return FakeResponse(status)

    async def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(
        collector_module.aiohttp,
        "ClientSession",
        FakeClientSession,
    )

    monkeypatch.setattr(
        collector_module.asyncio,
        "sleep",
        fake_sleep,
    )

    collector = HTTPCollector(
        timeout_seconds=5,
        max_retries=3,
    )

    evidence = await collector.check_platform(
        entity_type=EntityType.USERNAME,
        raw_value="testuser",
        normalized_value="testuser",
        source_name="GitHub",
        platform_config=PLATFORMS["GitHub"],
    )

    assert evidence.status == StatusEnum.ERROR
    assert evidence.details["http_status"] == 503
    assert state["requests"] == 4
    assert sleep_calls == [2, 4, 8]
