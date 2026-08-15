from core.detectors import (
    DevToDetector,
    HackerNewsDetector,
    StatusCodeDetector,
    TelegramDetector,
)
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


def test_github_login_is_used_as_username():
    response_data = {
        "login": "octocat",
        "name": "The Octocat",
        "public_repos": 8,
    }

    status, confidence, details = StatusCodeDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["username"] == "octocat"


def test_hackernews_user_is_found():
    response_data = {
        "id": "pg",
        "karma": 155000,
        "created": 1160418092,
        "about": "Example profile",
    }

    status, confidence, details = HackerNewsDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["username"] == "pg"
    assert details["karma"] == 155000
    assert details["created_at"] == "2006-10-09T18:21:32+00:00"


def test_hackernews_missing_data_is_unknown():
    status, confidence, details = HackerNewsDetector.detect(
        200,
        None,
    )

    assert status == StatusEnum.UNKNOWN
    assert confidence == ConfidenceLevel.LOW
    assert details == {}


def test_devto_user_is_found():
    response_data = {
        "type_of": "user",
        "username": "ben",
        "name": "Ben Halpern",
        "github_username": "benhalpern",
        "joined_at": "Dec 27, 2015",
        "location": "NY",
    }

    status, confidence, details = DevToDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["username"] == "ben"
    assert details["name"] == "Ben Halpern"
    assert details["github_username"] == "benhalpern"
    assert details["created_at"] == "Dec 27, 2015"


def test_devto_404_is_not_found():
    response_data = {
        "error": "not found",
        "status": 404,
    }

    status, confidence, details = DevToDetector.detect(
        404,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {}


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
