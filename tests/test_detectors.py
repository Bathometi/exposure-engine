from core.detectors import (
    KeybaseDetector,
    LichessDetector,
    DevToDetector,
    HackerNewsDetector,
    GravatarDetector,
    HIBPDetector,
    GitHubCommitDetector,
    OpenPGPDetector,
    ChessComDetector,
    HuggingFaceDetector,
    StatusCodeDetector,
    TelegramDetector,
    YouTubeDetector,
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


def test_lichess_user_is_found():
    response_data = {
        "id": "thibault",
        "username": "thibault",
    }

    status, confidence, details = LichessDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["username"] == "thibault"


def test_lichess_404_is_not_found():
    response_data = {
        "error": "Not found",
    }

    status, confidence, details = LichessDetector.detect(
        404,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {}


def test_huggingface_user_is_found():
    response_data = {
        "user": "osanseviero",
        "type": "user",
        "fullname": "Omar Sanseviero",
        "createdAt": "2021-02-21T15:45:50.000Z",
        "details": "Llamas, model merging, massive ASR for data",
        "numModels": 302,
        "numDatasets": 39,
        "numSpaces": 179,
        "numFollowers": 3494,
    }

    status, confidence, details = HuggingFaceDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["username"] == "osanseviero"
    assert details["name"] == "Omar Sanseviero"
    assert details["created_at"] == "2021-02-21T15:45:50.000Z"
    assert details["about"] == (
        "Llamas, model merging, massive ASR for data"
    )
    assert details["num_models"] == 302
    assert details["num_datasets"] == 39
    assert details["num_spaces"] == 179
    assert details["num_followers"] == 3494


def test_huggingface_404_is_not_found():
    response_data = {
        "error": "This user does not exist",
    }

    status, confidence, details = HuggingFaceDetector.detect(
        404,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {}


def test_huggingface_200_without_user_markers_is_unknown():
    response_data = {
        "type": "organization",
        "user": "example",
    }

    status, confidence, details = HuggingFaceDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.UNKNOWN
    assert confidence == ConfidenceLevel.LOW
    assert details == {}


def test_chesscom_user_is_found():
    response_data = {
        "player_id": 15448422,
        "username": "hikaru",
        "name": "Hikaru Nakamura",
        "title": "GM",
        "followers": 1406300,
        "location": "Florida",
        "joined": 1389043258,
        "status": "premium",
        "is_streamer": True,
        "twitch_url": "https://twitch.tv/gmhikaru",
        "verified": False,
        "league": "Legend",
    }

    status, confidence, details = ChessComDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["username"] == "hikaru"
    assert details["name"] == "Hikaru Nakamura"
    assert details["title"] == "GM"
    assert details["followers"] == 1406300
    assert details["location"] == "Florida"
    assert details["status"] == "premium"
    assert details["is_streamer"] is True
    assert details["twitch_url"] == "https://twitch.tv/gmhikaru"
    assert details["verified"] is False
    assert details["league"] == "Legend"


def test_chesscom_404_is_not_found():
    response_data = {
        "code": 0,
        "message": 'User "qzxvbnm847362910" not found.',
    }

    status, confidence, details = ChessComDetector.detect(
        404,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {}


def test_chesscom_200_without_user_markers_is_unknown():
    response_data = {
        "message": "Unexpected response",
    }

    status, confidence, details = ChessComDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.UNKNOWN
    assert confidence == ConfidenceLevel.LOW
    assert details == {}


def test_gravatar_profile_is_found():
    response_data = {
        "hash": (
            "99511d6010af8c574c31f94e1b327bba"
            "5e25086dd7b92a4b6f3e132b579cc8d1"
        ),
        "display_name": "Example",
        "profile_url": "https://gravatar.com/examplefork",
        "avatar_url": "https://0.gravatar.com/avatar/example",
        "location": "E.G.",
        "description": (
            "Sorry, this is not my name. "
            "Just an example, you know."
        ),
        "job_title": "Chief",
        "company": "EG Inc",
    }

    status, confidence, details = GravatarDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["hash"] == response_data["hash"]
    assert details["name"] == "Example"
    assert details["profile_url"] == (
        "https://gravatar.com/examplefork"
    )
    assert details["location"] == "E.G."
    assert details["job_title"] == "Chief"
    assert details["company"] == "EG Inc"


def test_gravatar_404_is_not_found():
    response_data = {
        "error": "Profile not found",
    }

    status, confidence, details = GravatarDetector.detect(
        404,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {}


def test_gravatar_200_without_profile_markers_is_unknown():
    response_data = {
        "message": "Unexpected response",
    }

    status, confidence, details = GravatarDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.UNKNOWN
    assert confidence == ConfidenceLevel.LOW
    assert details == {}
def test_hibp_breach_is_found():
    response_data = [
        {
            "Name": "Adobe",
        }
    ]

    status, confidence, details = HIBPDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["breach_count"] == 1
    assert details["breaches"] == ["Adobe"]
def test_hibp_404_is_not_found():
    status, confidence, details = HIBPDetector.detect(
        404,
        None,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {}
def test_hibp_429_is_rate_limited():
    status, confidence, details = HIBPDetector.detect(
        429,
        None,
    )

    assert status == StatusEnum.RATE_LIMITED
    assert confidence == ConfidenceLevel.MEDIUM
    assert details == {}
def test_hibp_403_is_blocked():
    status, confidence, details = HIBPDetector.detect(
        403,
        None,
    )

    assert status == StatusEnum.BLOCKED
    assert confidence == ConfidenceLevel.MEDIUM
    assert details == {}
def test_hibp_empty_200_is_unknown():
    status, confidence, details = HIBPDetector.detect(
        200,
        [],
    )

    assert status == StatusEnum.UNKNOWN
    assert confidence == ConfidenceLevel.LOW
    assert details == {}
def test_hibp_401_is_error():
    status, confidence, details = HIBPDetector.detect(
        401,
        None,
    )

    assert status == StatusEnum.ERROR
    assert confidence == ConfidenceLevel.LOW
    assert details == {}



def test_github_commit_search_is_found():
    response_data = {
        "total_count": 2,
        "incomplete_results": False,
        "items": [
            {
                "sha": "abc123",
                "html_url": "https://github.com/example/repo-one/commit/abc123",
                "commit": {
                    "author": {
                        "name": "Example User",
                        "email": "user@example.com",
                        "date": "2026-08-20T10:00:00Z",
                    },
                    "message": "First commit",
                },
                "author": {
                    "login": "example-user",
                },
                "repository": {
                    "full_name": "example/repo-one",
                },
            },
            {
                "sha": "def456",
                "html_url": "https://github.com/example/repo-two/commit/def456",
                "commit": {
                    "author": {
                        "name": "Example User",
                        "email": "user@example.com",
                        "date": "2026-08-21T10:00:00Z",
                    },
                    "message": "Second commit",
                },
                "author": {
                    "login": "example-user",
                },
                "repository": {
                    "full_name": "example/repo-two",
                },
            },
        ],
    }

    status, confidence, details = GitHubCommitDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details["commit_count"] == 2
    assert details["linked_users"] == ["example-user"]
    assert details["repositories"] == [
        "example/repo-one",
        "example/repo-two",
    ]
    assert details["sample_commits"] == [
        {
            "repository": "example/repo-one",
            "sha": "abc123",
            "author_date": "2026-08-20T10:00:00Z",
            "url": "https://github.com/example/repo-one/commit/abc123",
        },
        {
            "repository": "example/repo-two",
            "sha": "def456",
            "author_date": "2026-08-21T10:00:00Z",
            "url": "https://github.com/example/repo-two/commit/def456",
        },
    ]



def test_github_commit_search_empty_is_not_found():
    response_data = {
        "total_count": 0,
        "incomplete_results": False,
        "items": [],
    }

    status, confidence, details = GitHubCommitDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {
        "commit_count": 0,
        "linked_users": [],
        "repositories": [],
    }



def test_github_commit_search_429_is_rate_limited():
    status, confidence, details = GitHubCommitDetector.detect(
        429,
        None,
    )

    assert status == StatusEnum.RATE_LIMITED
    assert confidence == ConfidenceLevel.MEDIUM
    assert details == {}



def test_github_commit_search_403_rate_limit_is_rate_limited():
    response_data = {
        "message": "API rate limit exceeded"
    }

    status, confidence, details = GitHubCommitDetector.detect(
        403,
        response_data,
    )

    assert status == StatusEnum.RATE_LIMITED
    assert confidence == ConfidenceLevel.MEDIUM
    assert details == {}



def test_github_commit_search_403_is_blocked():
    response_data = {
        "message": "Resource access denied"
    }

    status, confidence, details = GitHubCommitDetector.detect(
        403,
        response_data,
    )

    assert status == StatusEnum.BLOCKED
    assert confidence == ConfidenceLevel.MEDIUM
    assert details == {}



def test_openpgp_200_is_found():
    response_data = (
        "-----BEGIN PGP PUBLIC KEY BLOCK-----\n"
        "example\n"
        "-----END PGP PUBLIC KEY BLOCK-----"
    )

    status, confidence, details = OpenPGPDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {
        "public_key_available": True,
    }



def test_openpgp_404_is_not_found():
    status, confidence, details = OpenPGPDetector.detect(
        404,
        None,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {
        "public_key_available": False,
    }



def test_openpgp_429_is_rate_limited():
    status, confidence, details = OpenPGPDetector.detect(
        429,
        None,
    )

    assert status == StatusEnum.RATE_LIMITED
    assert confidence == ConfidenceLevel.MEDIUM
    assert details == {}
def test_youtube_200_with_channel_is_found():
    response_data = {
        "items": [
            {
                "id": "UC123456",
                "snippet": {
                    "title": "Example Channel",
                    "description": "Public channel description",
                    "customUrl": "@somehandle",
                    "publishedAt": "2020-01-02T03:04:05Z",
                },
                "statistics": {
                    "viewCount": "1234",
                    "subscriberCount": "56",
                    "videoCount": "7",
                },
            }
        ]
    }

    status, confidence, details = YouTubeDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {
        "channel_id": "UC123456",
        "title": "Example Channel",
        "description": "Public channel description",
        "custom_url": "@somehandle",
        "published_at": "2020-01-02T03:04:05Z",
        "view_count": "1234",
        "subscriber_count": "56",
        "video_count": "7",
    }
def test_youtube_200_without_channel_is_not_found():
    response_data = {
        "items": []
    }

    status, confidence, details = YouTubeDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {
        "channel_found": False,
    }
def test_youtube_429_is_rate_limited():
    status, confidence, details = YouTubeDetector.detect(
        429,
        None,
    )

    assert status == StatusEnum.RATE_LIMITED
    assert confidence == ConfidenceLevel.MEDIUM
    assert details == {}
def test_youtube_200_zero_total_results_is_not_found():
    response_data = {
        "kind": "youtube#channelListResponse",
        "pageInfo": {
            "totalResults": 0,
            "resultsPerPage": 0,
        },
    }

    status, confidence, details = YouTubeDetector.detect(
        200,
        response_data,
    )

    assert status == StatusEnum.NOT_FOUND
    assert confidence == ConfidenceLevel.HIGH
    assert details == {
        "channel_found": False,
    }
