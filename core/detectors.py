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
