import html
import re

from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from core.schema import ConfidenceLevel, StatusEnum


class BaseDetector:
    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        raise NotImplementedError


class StatusCodeDetector(BaseDetector):
    """
    Детектор для REST/JSON API:
    GitHub, GitLab, DockerHub, Reddit.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        if status_code == 200:
            if isinstance(response_data, dict):
                details["name"] = response_data.get("name")

                details["username"] = (
                    response_data.get("username")
                    or response_data.get("login")
                )

                details["created_at"] = response_data.get(
                    "created_at"
                )

                details["public_repos"] = response_data.get(
                    "public_repos"
                )

                return (
                    StatusEnum.FOUND,
                    ConfidenceLevel.HIGH,
                    details,
                )

            if isinstance(response_data, list):
                if len(response_data) == 0:
                    return (
                        StatusEnum.NOT_FOUND,
                        ConfidenceLevel.HIGH,
                        details,
                    )

                user = response_data[0]

                if isinstance(user, dict):
                    details["name"] = user.get("name")
                    details["username"] = user.get("username")
                    details["created_at"] = user.get(
                        "created_at"
                    )

                return (
                    StatusEnum.FOUND,
                    ConfidenceLevel.HIGH,
                    details,
                )

            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        return (
            StatusEnum.UNKNOWN,
            ConfidenceLevel.LOW,
            details,
        )


class HackerNewsDetector(BaseDetector):
    """
    Детектор для публічного Hacker News API.

    API показує лише користувачів з публічною активністю.
    Тому відсутність даних не доводить відсутність акаунта.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        username = response_data.get("id")

        if not username:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        details["username"] = username
        details["karma"] = response_data.get("karma")

        created_timestamp = response_data.get("created")

        if created_timestamp is not None:
            details["created_at"] = datetime.fromtimestamp(
                created_timestamp,
                tz=timezone.utc,
            ).isoformat()

        details["about"] = response_data.get("about")

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            details,
        )


class DevToDetector(BaseDetector):
    """
    Детектор для публічного DEV Community API.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if response_data.get("type_of") != "user":
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        username = response_data.get("username")

        if not username:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        details["username"] = username
        details["name"] = response_data.get("name")
        details["created_at"] = response_data.get("joined_at")
        details["github_username"] = response_data.get(
            "github_username"
        )
        details["twitter_username"] = response_data.get(
            "twitter_username"
        )
        details["location"] = response_data.get("location")
        details["website_url"] = response_data.get("website_url")
        details["summary"] = response_data.get("summary")

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            details,
        )


def _extract_telegram_display_name(
    html_text: str,
) -> str | None:
    match = re.search(
        (
            r'<div[^>]*class=["\'][^"\']*'
            r'tgme_page_title[^"\']*["\'][^>]*>'
            r'(.*?)</div>'
        ),
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if match is None:
        return None

    value = re.sub(
        r"<[^>]+>",
        "",
        match.group(1),
    )

    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()

    return value or None


class TelegramDetector(BaseDetector):
    """
    Детектор для публічних Telegram-сторінок t.me/username.
    """

    @staticmethod
    def detect(
        status_code: int,
        html_text: str,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if not isinstance(html_text, str):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        html_lower = html_text.lower()

        has_title = (
            'class="tgme_page_title"' in html_lower
        )

        has_extra = (
            'class="tgme_page_extra"' in html_lower
        )

        if has_title or has_extra:
            details["profile_marker"] = (
                "tgme_page_title"
                if has_title
                else "tgme_page_extra"
            )

            if has_title:
                display_name = (
                    _extract_telegram_display_name(
                        html_text
                    )
                )

                if display_name:
                    details["display_name"] = (
                        display_name
                    )

            return (
                StatusEnum.FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        return (
            StatusEnum.UNKNOWN,
            ConfidenceLevel.LOW,
            details,
        )

class CodebergDetector(BaseDetector):
    """
    Детектор для публічного Codeberg API.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        username = (
            response_data.get("username")
            or response_data.get("login")
        )

        if not username:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        details["username"] = username
        details["name"] = response_data.get("full_name")
        details["created_at"] = response_data.get("created")
        details["website_url"] = response_data.get("website")
        details["location"] = response_data.get("location")
        details["about"] = response_data.get("description")
        details["followers_count"] = response_data.get(
            "followers_count"
        )
        details["following_count"] = response_data.get(
            "following_count"
        )
        details["visibility"] = response_data.get("visibility")

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            details,
        )
class KeybaseDetector(BaseDetector):
    """
    Детектор для публічного Keybase API.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        api_status = response_data.get("status")

        if not isinstance(api_status, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        status_code_api = api_status.get("code")
        status_name = api_status.get("name")

        if (
            status_code_api == 205
            and status_name == "NOT_FOUND"
        ):
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        if (
            status_code_api != 0
            or status_name != "OK"
        ):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        user_data = response_data.get("them")

        if not isinstance(user_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        basics = user_data.get("basics", {})
        profile = user_data.get("profile", {})

        if not isinstance(basics, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        username = basics.get("username")

        if not username:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        details["username"] = username

        if isinstance(profile, dict):
            details["name"] = profile.get("full_name")
            details["location"] = profile.get("location")
            details["about"] = profile.get("bio")

        created_timestamp = basics.get("ctime")

        if created_timestamp is not None:
            details["created_at"] = datetime.fromtimestamp(
                created_timestamp,
                tz=timezone.utc,
            ).isoformat()

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            details,
        )


class LichessDetector(BaseDetector):
    """
    Детектор для публічного Lichess API.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        username = (
            response_data.get("username")
            or response_data.get("id")
        )

        if not username:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        details["username"] = username

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            details,
        )


class HuggingFaceDetector(BaseDetector):
    """
    Detector for public Hugging Face user profiles.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if response_data.get("type") != "user":
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        username = response_data.get("user")

        if not username:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        details["username"] = username

        optional_fields = {
            "name": response_data.get("fullname"),
            "created_at": response_data.get("createdAt"),
            "about": response_data.get("details"),
            "num_models": response_data.get("numModels"),
            "num_datasets": response_data.get("numDatasets"),
            "num_spaces": response_data.get("numSpaces"),
            "num_followers": response_data.get("numFollowers"),
        }

        for key, value in optional_fields.items():
            if value is not None and value != "":
                details[key] = value

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            details,
        )


class ChessComDetector(BaseDetector):
    """
    Detector for public Chess.com player profiles.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        username = response_data.get("username")
        player_id = response_data.get("player_id")

        if not username or not player_id:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        details["username"] = username
        details["player_id"] = player_id

        optional_fields = {
            "name": response_data.get("name"),
            "title": response_data.get("title"),
            "followers": response_data.get("followers"),
            "location": response_data.get("location"),
            "status": response_data.get("status"),
            "is_streamer": response_data.get("is_streamer"),
            "twitch_url": response_data.get("twitch_url"),
            "verified": response_data.get("verified"),
            "league": response_data.get("league"),
        }

        joined = response_data.get("joined")

        if isinstance(joined, (int, float)):
            details["created_at"] = datetime.fromtimestamp(
                joined,
                tz=timezone.utc,
            ).isoformat()

        for key, value in optional_fields.items():
            if value is not None and value != "":
                details[key] = value

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            details,
        )


class GravatarDetector(BaseDetector):
    """
    Detector for public Gravatar profiles.

    FOUND means that a public Gravatar profile was found
    for the supplied profile identifier.

    It does not prove that the email mailbox exists
    or is deliverable.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        details = {}

        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                details,
            )

        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                details,
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        profile_hash = response_data.get("hash")
        profile_url = response_data.get("profile_url")

        if not profile_hash or not profile_url:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                details,
            )

        details["hash"] = profile_hash
        details["profile_url"] = profile_url

        optional_fields = {
            "name": response_data.get("display_name"),
            "avatar_url": response_data.get("avatar_url"),
            "location": response_data.get("location"),
            "about": response_data.get("description"),
            "job_title": response_data.get("job_title"),
            "company": response_data.get("company"),
        }

        for key, value in optional_fields.items():
            if value is not None and value != "":
                details[key] = value

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            details,
        )


class HIBPDetector(BaseDetector):
    """
    Detector for Have I Been Pwned breach results.
    """

    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                {},
            )
        if status_code == 401:
            return (
                StatusEnum.ERROR,
                ConfidenceLevel.LOW,
                {},
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                {},
            )
        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                {},
            )
        if (
            status_code == 200
            and isinstance(response_data, list)
            and response_data
        ):
            breaches = [
                item["Name"]
                for item in response_data
                if isinstance(item, dict)
                and item.get("Name")
            ]

            if breaches:
                return (
                    StatusEnum.FOUND,
                    ConfidenceLevel.HIGH,
                    {
                        "breach_count": len(breaches),
                        "breaches": breaches,
                    },
                )

        return (
            StatusEnum.UNKNOWN,
            ConfidenceLevel.LOW,
            {},
        )


class GitHubCommitDetector(BaseDetector):
    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                {},
            )

        if (
            status_code == 403
            and isinstance(response_data, dict)
            and "rate limit" in str(
                response_data.get("message", "")
            ).lower()
        ):
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                {},
            )

        if status_code == 403:
            return (
                StatusEnum.BLOCKED,
                ConfidenceLevel.MEDIUM,
                {},
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                {},
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                {},
            )

        total_count = response_data.get(
            "total_count"
        )
        items = response_data.get(
            "items"
        )

        if (
            not isinstance(total_count, int)
            or not isinstance(items, list)
        ):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                {},
            )

        if total_count == 0:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                {
                    "commit_count": 0,
                    "linked_users": [],
                    "repositories": [],
                },
            )

        if total_count < 0 or not items:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                {},
            )

        repositories = []
        linked_users = []
        sample_commits = []

        for item in items:
            if not isinstance(item, dict):
                continue

            full_name = None
            repository = item.get("repository")

            if isinstance(repository, dict):
                full_name = repository.get(
                    "full_name"
                )

                if (
                    full_name
                    and full_name not in repositories
                ):
                    repositories.append(
                        full_name
                    )

            author = item.get("author")

            if isinstance(author, dict):
                login = author.get("login")

                if (
                    login
                    and login not in linked_users
                ):
                    linked_users.append(
                        login
                    )

            commit = item.get("commit")
            commit_author = (
                commit.get("author")
                if isinstance(commit, dict)
                else None
            )
            author_date = (
                commit_author.get("date")
                if isinstance(commit_author, dict)
                else None
            )
            sha = item.get("sha")
            url = item.get("html_url")

            if (
                len(sample_commits) < 5
                and full_name
                and sha
                and author_date
                and url
            ):
                sample_commits.append(
                    {
                        "repository": full_name,
                        "sha": sha,
                        "author_date": author_date,
                        "url": url,
                    }
                )

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            {
                "commit_count": total_count,
                "linked_users": linked_users,
                "repositories": repositories,
                "sample_commits": sample_commits,
            },
        )

class OpenPGPDetector(BaseDetector):
    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                {},
            )

        if status_code == 404:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                {
                    "public_key_available": False,
                },
            )

        if (
            status_code == 200
            and isinstance(response_data, str)
            and "-----BEGIN PGP PUBLIC KEY BLOCK-----" in response_data
            and "-----END PGP PUBLIC KEY BLOCK-----" in response_data
        ):
            return (
                StatusEnum.FOUND,
                ConfidenceLevel.HIGH,
                {
                    "public_key_available": True,
                },
            )

        return (
            StatusEnum.UNKNOWN,
            ConfidenceLevel.LOW,
            {},
        )


class YouTubeDetector(BaseDetector):
    @staticmethod
    def detect(
        status_code: int,
        response_data: Any,
    ) -> Tuple[
        StatusEnum,
        ConfidenceLevel,
        Dict[str, Any],
    ]:
        if status_code == 429:
            return (
                StatusEnum.RATE_LIMITED,
                ConfidenceLevel.MEDIUM,
                {},
            )

        if status_code != 200:
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                {},
            )

        if not isinstance(response_data, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                {},
            )

        page_info = response_data.get("pageInfo")

        if (
            isinstance(page_info, dict)
            and page_info.get("totalResults") == 0
        ):
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                {
                    "channel_found": False,
                },
            )

        items = response_data.get("items")

        if not isinstance(items, list):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                {},
            )

        if not items:
            return (
                StatusEnum.NOT_FOUND,
                ConfidenceLevel.HIGH,
                {
                    "channel_found": False,
                },
            )

        channel = items[0]

        if not isinstance(channel, dict):
            return (
                StatusEnum.UNKNOWN,
                ConfidenceLevel.LOW,
                {},
            )

        snippet = channel.get("snippet", {})
        statistics = channel.get("statistics", {})

        if not isinstance(snippet, dict):
            snippet = {}

        if not isinstance(statistics, dict):
            statistics = {}

        return (
            StatusEnum.FOUND,
            ConfidenceLevel.HIGH,
            {
                "channel_id": channel.get("id"),
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "custom_url": snippet.get("customUrl"),
                "published_at": snippet.get("publishedAt"),
                "view_count": statistics.get("viewCount"),
                "subscriber_count": statistics.get(
                    "subscriberCount"
                ),
                "video_count": statistics.get("videoCount"),
            },
        )
