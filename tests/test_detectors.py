from core.detectors import StatusCodeDetector, TelegramDetector
from core.schema import StatusEnum, ConfidenceLevel


def test_404_is_not_found():
    status, confidence, details = StatusCodeDetector.detect(
        404,
        None,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH


def test_403_is_blocked():
    status, confidence, details = StatusCodeDetector.detect(
        403,
        None,
    )

    assert status == StatusEnum.BLOCKED
    assert confidence == ConfidenceLevel.MEDIUM


def test_429_is_rate_limited():
    status, confidence, details = StatusCodeDetector.detect(
        429,
        None,
    )

    assert status == StatusEnum.RATE_LIMITED
    assert confidence == ConfidenceLevel.MEDIUM


def test_gitlab_empty_list_is_not_found():
    status, confidence, details = StatusCodeDetector.detect(
        200,
        [],
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH


def test_telegram_marker_is_found():
    html = '<div class="tgme_page_title">Test User</div>'

    status, confidence, details = TelegramDetector.detect(
        200,
        html,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH


def test_telegram_without_marker_is_unknown():
    html = "<html><body>Nothing useful here</body></html>"

    status, confidence, details = TelegramDetector.detect(
        200,
        html,
    )

    assert status == StatusEnum.UNKNOWN
    assert confidence == ConfidenceLevel.LOW
