from typing import Dict, Any, Tuple
from core.schema import StatusEnum, ConfidenceLevel


class BaseDetector:
    @staticmethod
    def detect(status_code: int, response_data: Any) -> Tuple[StatusEnum, ConfidenceLevel, Dict[str, Any]]:
        raise NotImplementedError


class StatusCodeDetector(BaseDetector):
    """Детектор для REST API (GitHub, DockerHub, GitLab)."""
    @staticmethod
    def detect(status_code: int, response_data: Any) -> Tuple[StatusEnum, ConfidenceLevel, Dict[str, Any]]:
        details = {}
        if status_code == 200:
            if isinstance(response_data, dict):
                details["name"] = response_data.get("name")
                details["created_at"] = response_data.get("created_at")
                details["public_repos"] = response_data.get("public_repos")
            elif isinstance(response_data, list) and len(response_data) > 0:
                # Наприклад, для GitLab API, який повертає масив користувачів
                user = response_data[0]
                details["name"] = user.get("name")
                details["username"] = user.get("username")
                details["created_at"] = user.get("created_at")
            return StatusEnum.FOUND, ConfidenceLevel.HIGH, details
        elif status_code == 404:
            return StatusEnum.NOT_FOUND, ConfidenceLevel.HIGH, details
        elif status_code == 429:
            return StatusEnum.RATE_LIMITED, ConfidenceLevel.MEDIUM, details
        elif status_code == 403:
            return StatusEnum.BLOCKED, ConfidenceLevel.MEDIUM, details
        return StatusEnum.UNKNOWN, ConfidenceLevel.LOW, details


class TelegramDetector(BaseDetector):
    """Спеціалізований маркерний детектор для Telegram Web (t.me/username)."""
    @staticmethod
    def detect(status_code: int, html_text: str) -> Tuple[StatusEnum, ConfidenceLevel, Dict[str, Any]]:
        details = {}
        if status_code != 200 or not isinstance(html_text, str):
            if status_code == 429:
                return StatusEnum.RATE_LIMITED, ConfidenceLevel.MEDIUM, details
            elif status_code == 403:
                return StatusEnum.BLOCKED, ConfidenceLevel.MEDIUM, details
            return StatusEnum.UNKNOWN, ConfidenceLevel.LOW, details

        html_lower = html_text.lower()

        # Позитивні докази існування акаунта / каналу / групи:
        # На існуючих сторінках t.me є елементи tgme_page_title або tgme_page_extra
        has_title = 'class="tgme_page_title"' in html_lower
        has_extra = 'class="tgme_page_extra"' in html_lower
        has_action_button = 'tgme_action_button' in html_lower

        if has_title or has_extra or has_action_button:
            return StatusEnum.FOUND, ConfidenceLevel.HIGH, details

        # Якщо позитивних елементів профілю немає
        return StatusEnum.NOT_FOUND, ConfidenceLevel.HIGH, details
