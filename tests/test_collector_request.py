import pytest

import core.collector as collector_module
from core.collector import HTTPCollector


@pytest.mark.asyncio
async def test_request_returns_parsed_json(monkeypatch):
    class FakeResponse:
        status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def json(self):
            return {
                "items": [
                    {
                        "id": {
                            "channelId": "UC111",
                        }
                    }
                ]
            }

    class FakeClientSession:
        last_get_kwargs = None

        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(
            self,
            url,
            headers=None,
            params=None,
            allow_redirects=True,
        ):
            FakeClientSession.last_get_kwargs = {
                "url": url,
                "headers": headers,
                "params": params,
                "allow_redirects": allow_redirects,
            }
            return FakeResponse()

    monkeypatch.setattr(
        collector_module.aiohttp,
        "ClientSession",
        FakeClientSession,
    )

    collector = HTTPCollector(max_retries=0)

    result = await collector.request(
        url="https://example.test/search",
        response_type="json",
        headers={"X-Test": "yes"},
        params={"q": "TEST_USERNAME"},
    )

    assert result.status_code == 200
    assert result.response_data == {
        "items": [
            {
                "id": {
                    "channelId": "UC111",
                }
            }
        ]
    }
    assert result.error is None

    assert FakeClientSession.last_get_kwargs == {
        "url": "https://example.test/search",
        "headers": {"X-Test": "yes"},
        "params": {"q": "TEST_USERNAME"},
        "allow_redirects": True,
    }
@pytest.mark.asyncio
async def test_request_retries_retryable_status(monkeypatch):
    statuses = [503, 200]
    sleep_calls = []
    state = {"requests": 0}

    class FakeResponse:
        def __init__(self, status):
            self.status = status

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def json(self):
            return {"ok": True}

    class FakeClientSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(
            self,
            url,
            headers=None,
            params=None,
            allow_redirects=True,
        ):
            state["requests"] += 1
            return FakeResponse(statuses.pop(0))

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

    collector = HTTPCollector(max_retries=1)

    result = await collector.request(
        url="https://example.test/search",
        response_type="json",
    )

    assert result.status_code == 200
    assert result.response_data == {"ok": True}
    assert result.error is None
    assert state["requests"] == 2
    assert sleep_calls == [2]
@pytest.mark.asyncio
async def test_request_retries_timeout_then_succeeds(monkeypatch):
    sleep_calls = []
    state = {"requests": 0}

    class FakeResponse:
        status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def json(self):
            return {"ok": True}

    class FakeClientSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(
            self,
            url,
            headers=None,
            params=None,
            allow_redirects=True,
        ):
            state["requests"] += 1

            if state["requests"] == 1:
                raise collector_module.asyncio.TimeoutError()

            return FakeResponse()

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

    collector = HTTPCollector(max_retries=1)

    result = await collector.request(
        url="https://example.test/search",
        response_type="json",
    )

    assert result.status_code == 200
    assert result.response_data == {"ok": True}
    assert result.error is None
    assert state["requests"] == 2
    assert sleep_calls == [2]
