import pytest

from config.platforms import PLATFORMS

from core.collector import HTTPCollector
from core.detector_registry import DETECTOR_REGISTRY
from core.detectors import StatusCodeDetector
from core.schema import (
    ConfidenceLevel,
    EntityType,
    StatusEnum,
)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_check_platform_github():
    collector = HTTPCollector(
        timeout_seconds=5
    )

    # Реальна перевірка валідного GitHub акаунта.
    evidence = await collector.check_platform(
        entity_type=EntityType.USERNAME,
        raw_value="octocat",
        normalized_value="octocat",
        source_name="GitHub",
        platform_config=PLATFORMS["GitHub"],
    )

    assert evidence.status == StatusEnum.FOUND
    assert evidence.source_name == "GitHub"
    assert "target_url" in evidence.details


@pytest.mark.asyncio
async def test_unknown_detector_returns_error():
    collector = HTTPCollector()

    bad_config = {
        "url_template": (
            "https://example.test/users/{username}"
        ),
        "detector": "does_not_exist",
    }

    evidence = await collector.check_platform(
        entity_type=EntityType.USERNAME,
        raw_value="testuser",
        normalized_value="testuser",
        source_name="BrokenPlatform",
        platform_config=bad_config,
    )

    assert evidence.status == StatusEnum.ERROR
    assert evidence.confidence == ConfidenceLevel.LOW
    assert (
        evidence.details["error"]
        == "Unknown detector: does_not_exist"
    )


class FakeResponse:
    """
    Фальшива HTTP-відповідь.
    Ніякого реального запиту в інтернет.
    """

    status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        pass


class FakeSession:
    """
    Фальшива aiohttp ClientSession.
    """
    last_get_kwargs = None

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        pass

    def get(
        self,
        *args,
        **kwargs,
    ):
        FakeSession.last_get_kwargs = kwargs
        return FakeResponse()


@pytest.mark.asyncio
async def test_invalid_response_type_returns_error(
    monkeypatch,
):
    collector = HTTPCollector()

    monkeypatch.setitem(
        DETECTOR_REGISTRY,
        "broken_response",
        {
            "detector": StatusCodeDetector,
            "response_type": "xml",
        },
    )

    monkeypatch.setattr(
        "core.collector.aiohttp.ClientSession",
        FakeSession,
    )

    bad_config = {
        "url_template": (
            "https://example.test/users/{username}"
        ),
        "detector": "broken_response",
    }

    evidence = await collector.check_platform(
        entity_type=EntityType.USERNAME,
        raw_value="testuser",
        normalized_value="testuser",
        source_name="BrokenPlatform",
        platform_config=bad_config,
    )

    assert evidence.status == StatusEnum.ERROR
    assert evidence.confidence == ConfidenceLevel.LOW
    assert (
        evidence.details["error"]
        == "Unsupported response type: xml"
    )


@pytest.mark.asyncio
async def test_collector_supports_async_context_manager():
    async with HTTPCollector() as collector:
        assert collector.session is not None

    assert collector.session is None
@pytest.mark.asyncio
async def test_collector_uses_identifier_for_target_url():
    collector = HTTPCollector()

    gravatar_config = {
        "url_template": (
            "https://api.gravatar.com/"
            "v3/profiles/{value}"
        ),
        "identifier": "gravatar_sha256",
        "detector": "does_not_exist",
    }

    evidence = await collector.check_platform(
        entity_type=EntityType.EMAIL,
        raw_value="User@Example.COM",
        normalized_value="user@example.com",
        source_name="Gravatar",
        platform_config=gravatar_config,
    )

    assert evidence.status == StatusEnum.ERROR

    assert evidence.details["target_url"] == (
        "https://api.gravatar.com/v3/profiles/"
        "b4c9a289323b21a01c3e940f150eb9b8"
        "c542587f1abfd8f0e1cc1ffc5e475514"
    )
def test_collector_resolves_headers_from_environment(
    monkeypatch,
):
    collector = HTTPCollector()

    monkeypatch.setenv(
        "HIBP_API_KEY",
        "test-api-key",
    )

    platform_config = {
        "headers_from_env": {
            "hibp-api-key": "HIBP_API_KEY",
        },
    }

    headers = collector._resolve_request_headers(
        platform_config
    )

    assert headers == {
        "hibp-api-key": "test-api-key",
    }
@pytest.mark.asyncio
async def test_collector_passes_env_headers_to_request(
    monkeypatch,
):
    collector = HTTPCollector()

    monkeypatch.setenv(
        "HIBP_API_KEY",
        "test-api-key",
    )

    monkeypatch.setitem(
        DETECTOR_REGISTRY,
        "header_test",
        {
            "detector": StatusCodeDetector,
            "response_type": "xml",
        },
    )

    monkeypatch.setattr(
        "core.collector.aiohttp.ClientSession",
        FakeSession,
    )

    FakeSession.last_get_kwargs = None

    platform_config = {
        "url_template": (
            "https://example.test/{value}"
        ),
        "detector": "header_test",
        "headers_from_env": {
            "hibp-api-key": "HIBP_API_KEY",
        },
    }

    await collector.check_platform(
        entity_type=EntityType.EMAIL,
        raw_value="user@example.com",
        normalized_value="user@example.com",
        source_name="HeaderTest",
        platform_config=platform_config,
    )

    assert FakeSession.last_get_kwargs["headers"] == {
        "hibp-api-key": "test-api-key",
    }
