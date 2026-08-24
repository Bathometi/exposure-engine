from config.platforms import (
    EMAIL_PLATFORMS,
    PLATFORMS,
)

from core.detector_registry import DETECTOR_REGISTRY
from core.detectors import (
    ChessComDetector,
    CodebergDetector,
    DevToDetector,
    HackerNewsDetector,
    GravatarDetector,
    HIBPDetector,
    GitHubCommitDetector,
    OpenPGPDetector,
    HuggingFaceDetector,
    KeybaseDetector,
    LichessDetector,
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


def test_lichess_is_registered_correctly():
    assert (
        DETECTOR_REGISTRY["lichess"]["detector"]
        is LichessDetector
    )

    assert (
        DETECTOR_REGISTRY["lichess"]["response_type"]
        == "json"
    )


def test_huggingface_is_registered_correctly():
    assert (
        DETECTOR_REGISTRY["huggingface"]["detector"]
        is HuggingFaceDetector
    )

    assert (
        DETECTOR_REGISTRY["huggingface"]["response_type"]
        == "json"
    )


def test_chesscom_is_registered_correctly():
    assert (
        DETECTOR_REGISTRY["chesscom"]["detector"]
        is ChessComDetector
    )

    assert (
        DETECTOR_REGISTRY["chesscom"]["response_type"]
        == "json"
    )
def test_gravatar_is_registered_correctly():
    assert (
        DETECTOR_REGISTRY["gravatar"]["detector"]
        is GravatarDetector
    )

    assert (
        DETECTOR_REGISTRY["gravatar"]["response_type"]
        == "json"
    )
def test_all_email_detectors_are_registered():
    for source_name, config in EMAIL_PLATFORMS.items():
        detector_name = config["detector"]

        assert detector_name in DETECTOR_REGISTRY, (
            f"{source_name} uses detector "
            f"'{detector_name}' which is not registered"
        )
def test_hibp_is_registered_correctly():
    assert (
        DETECTOR_REGISTRY["hibp"]["detector"]
        is HIBPDetector
    )

    assert (
        DETECTOR_REGISTRY["hibp"]["response_type"]
        == "json"
    )



def test_github_commits_is_registered_correctly():
    assert (
        DETECTOR_REGISTRY["github_commits"]["detector"]
        is GitHubCommitDetector
    )

    assert (
        DETECTOR_REGISTRY["github_commits"]["response_type"]
        == "json"
    )



def test_github_commits_email_source_is_configured():
    config = EMAIL_PLATFORMS["GitHub Commits"]

    assert config["url_template"] == (
        "https://api.github.com/search/commits"
    )
    assert config["detector"] == "github_commits"
    assert config["query_params"] == {
        "q": "author-email:{value}",
        "per_page": "100",
    }

def test_openpgp_is_registered_correctly():
    assert (
        DETECTOR_REGISTRY["openpgp"]["detector"]
        is OpenPGPDetector
    )

    assert (
        DETECTOR_REGISTRY["openpgp"]["response_type"]
        == "text"
    )


def test_openpgp_email_source_is_configured():
    config = EMAIL_PLATFORMS["OpenPGP"]

    assert config["url_template"] == (
        "https://keys.openpgp.org/vks/v1/by-email/{value}"
    )
    assert config["detector"] == "openpgp"
