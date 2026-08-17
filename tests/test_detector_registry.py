from config.platforms import PLATFORMS

from core.detector_registry import DETECTOR_REGISTRY
from core.detectors import (
    CodebergDetector,
    DevToDetector,
    HackerNewsDetector,
    KeybaseDetector,
    StatusCodeDetector,
    TelegramDetector,
)


def test_registry_maps_detectors_correctly():
    assert (
        DETECTOR_REGISTRY["status_code"]["detector"]
        is StatusCodeDetector
    )

    assert (
        DETECTOR_REGISTRY["telegram"]["detector"]
        is TelegramDetector
    )

    assert (
        DETECTOR_REGISTRY["hackernews"]["detector"]
        is HackerNewsDetector
    )

    assert (
        DETECTOR_REGISTRY["devto"]["detector"]
        is DevToDetector
    )


def test_registry_has_valid_response_types():
    allowed_response_types = {
        "json",
        "text",
    }

    for detector_name, config in DETECTOR_REGISTRY.items():
        assert "response_type" in config, (
            f"{detector_name} has no response_type"
        )

        assert config["response_type"] in allowed_response_types, (
            f"{detector_name} has invalid response_type"
        )


def test_telegram_uses_text_response():
    assert (
        DETECTOR_REGISTRY["telegram"]["response_type"]
        == "text"
    )


def test_all_platform_detectors_are_registered():
    for platform_name, config in PLATFORMS.items():
        detector_name = config["detector"]

        assert detector_name in DETECTOR_REGISTRY, (
            f"{platform_name} uses detector "
            f"'{detector_name}' which is not registered"
        )


def test_codeberg_is_registered_correctly():
    assert (
        DETECTOR_REGISTRY["codeberg"]["detector"]
        is CodebergDetector
    )

    assert (
        DETECTOR_REGISTRY["codeberg"]["response_type"]
        == "json"
    )


def test_keybase_is_registered_correctly():
    assert (
        DETECTOR_REGISTRY["keybase"]["detector"]
        is KeybaseDetector
    )

    assert (
        DETECTOR_REGISTRY["keybase"]["response_type"]
        == "json"
    )
