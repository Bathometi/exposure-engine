from core.detectors import (
    KeybaseDetector,
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
from core.detectors import CodebergDetector


def test_codeberg_user_is_found():
    response_data = {
        "id": 70422,
        "login": "forgejo",
        "username": "forgejo",
        "full_name": "Forgejo",
        "created": "2022-11-06T07:18:11+01:00",
        "website": "https://forgejo.org",
        "location": "",
        "description": "Beyond coding. We forge.",
        "visibility": "public",
        "followers_count": 586,
        "following_count": 0,
    }

    status, confidence, details = CodebergDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH

    assert details["username"] == "forgejo"
    assert details["name"] == "Forgejo"
    assert details["created_at"] == (
        "2022-11-06T07:18:11+01:00"
    )
    assert details["website_url"] == "https://forgejo.org"
    assert details["about"] == "Beyond coding. We forge."
    assert details["visibility"] == "public"


def test_codeberg_404_is_not_found():
    response_data = {
        "message": (
            "user redirect does not exist "
            "[name: qzxvbnm847362910]"
        )
    }

    status, confidence, details = CodebergDetector.detect(
        404,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {}
def test_keybase_user_is_found():
    response_data = {
        "status": {
            "code": 0,
            "name": "OK",
        },
        "them": {
            "basics": {
                "username": "max",
                "ctime": 1391657400,
            },
            "profile": {
                "full_name": "Max Krohn",
                "location": "New York, NY",
                "bio": "Keybase.io co-founder and developer",
            },
        },
    }

    status, confidence, details = KeybaseDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["username"] == "max"
    assert details["name"] == "Max Krohn"
    assert details["location"] == "New York, NY"
    assert details["created_at"] == "2014-02-06T03:30:00+00:00"


def test_keybase_api_not_found():
    response_data = {
        "status": {
            "code": 205,
            "desc": "maxtaco: user not found",
            "name": "NOT_FOUND",
        }
    }

    status, confidence, details = KeybaseDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {}
