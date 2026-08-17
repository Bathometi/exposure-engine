import pytest

from config.platforms import PLATFORMS
from core.detector_registry import DETECTOR_REGISTRY
from core.schema import ConfidenceLevel, StatusEnum


@pytest.mark.parametrize(
    (
        "platform_name",
        "status_code",
        "response_data",
        "expected_status",
        "expected_confidence",
    ),
    [
        (
            "GitHub",
            200,
            {
                "login": "octocat",
            },
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "GitLab",
            200,
            [
                {
                    "username": "root",
                }
            ],
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "DockerHub",
            200,
            {
                "username": "library",
            },
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "Reddit",
            403,
            None,
            StatusEnum.BLOCKED,
            ConfidenceLevel.MEDIUM,
        ),
        (
            "Telegram",
            200,
            '<div class="tgme_page_title">Test User</div>',
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "HackerNews",
            200,
            {
                "id": "pg",
                "karma": 100,
                "created": 1234567890,
            },
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "DevTo",
            200,
            {
                "type_of": "user",
                "username": "ben",
            },
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "Codeberg",
            200,
            {
                "username": "forgejo",
            },
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "Keybase",
            200,
            {
                "status": {
                    "code": 0,
                    "name": "OK",
                },
                "them": {
                    "basics": {
                        "username": "max",
                    },
                    "profile": {},
                },
            },
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "Lichess",
            200,
            {
                "id": "thibault",
                "username": "thibault",
            },
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "HuggingFace",
            200,
            {
                "user": "osanseviero",
                "type": "user",
                "fullname": "Omar Sanseviero",
            },
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
        ),
    ],
)
def test_platform_regression_matrix(
    platform_name,
    status_code,
    response_data,
    expected_status,
    expected_confidence,
):
    platform_config = PLATFORMS[platform_name]

    detector_name = platform_config["detector"]

    registry_entry = DETECTOR_REGISTRY[detector_name]

    detector = registry_entry["detector"]

    status, confidence, _ = detector.detect(
        status_code,
        response_data,
    )

    assert status == expected_status
    assert confidence == expected_confidence
@pytest.mark.parametrize(
    (
        "platform_name",
        "status_code",
        "response_data",
        "expected_status",
        "expected_confidence",
    ),
    [
        (
            "GitHub",
            404,
            None,
            StatusEnum.NOT_FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "GitLab",
            200,
            [],
            StatusEnum.NOT_FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "DockerHub",
            404,
            None,
            StatusEnum.NOT_FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "Reddit",
            403,
            None,
            StatusEnum.BLOCKED,
            ConfidenceLevel.MEDIUM,
        ),
        (
            "Telegram",
            200,
            "<html><body>No public profile markers</body></html>",
            StatusEnum.UNKNOWN,
            ConfidenceLevel.LOW,
        ),
        (
            "HackerNews",
            200,
            None,
            StatusEnum.UNKNOWN,
            ConfidenceLevel.LOW,
        ),
        (
            "DevTo",
            404,
            {
                "error": "not found",
                "status": 404,
            },
            StatusEnum.NOT_FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "Codeberg",
            404,
            {
                "message": "user does not exist",
            },
            StatusEnum.NOT_FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "Keybase",
            200,
            {
                "status": {
                    "code": 205,
                    "name": "NOT_FOUND",
                }
            },
            StatusEnum.NOT_FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "Lichess",
            404,
            {
                "error": "Not found",
            },
            StatusEnum.NOT_FOUND,
            ConfidenceLevel.HIGH,
        ),
        (
            "HuggingFace",
            404,
            {
                "error": "This user does not exist",
            },
            StatusEnum.NOT_FOUND,
            ConfidenceLevel.HIGH,
        ),
    ],
)
def test_platform_negative_regression_matrix(
    platform_name,
    status_code,
    response_data,
    expected_status,
    expected_confidence,
):
    platform_config = PLATFORMS[platform_name]

    detector_name = platform_config["detector"]

    registry_entry = DETECTOR_REGISTRY[detector_name]

    detector = registry_entry["detector"]

    status, confidence, _ = detector.detect(
        status_code,
        response_data,
    )

    assert status == expected_status
    assert confidence == expected_confidence
