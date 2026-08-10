from typing import Dict, Any, Tuple
from core.schema import StatusEnum, ConfidenceLevel


class BaseDetector:
    """Базовий клас для всіх детекторів."""
    @staticmethod
    def detect(status_code: int, response_data: Any) -> Tuple[StatusEnum, ConfidenceLevel, Dict[str, Any]]:
        raise NotImplementedError


class StatusCodeDetector(BaseDetector):
    """Детектор для стандартних REST API (GitHub, DockerHub), де status code є вирішальним."""
    @staticmethod
    def detect(status_code: int, response_data: Any) -> Tuple[StatusEnum, ConfidenceLevel, Dict[str, Any]]:
        details = {}
        if status_code == 200:
            if isinstance(response_data, dict):
                # Забираємо тільки ключові метадані, як радив ментор (без всього raw_json)
                details["name"] = response_data.get("name")
                details["created_at"] = response_data.get("created_at")
                details["public_repos"] = response_data.get("public_repos")
            return StatusEnum.FOUND, ConfidenceLevel.HIGH, details
        elif status_code == 404:
            return StatusEnum.NOT_FOUND, ConfidenceLevel.HIGH, details
        elif status_code in (429, 403):
            return StatusEnum.RATE_LIMITED, ConfidenceLevel.LOW, details
        return StatusEnum.ERROR, ConfidenceLevel.LOW, details


class HTMLMarkerDetector(BaseDetector):
    """Детектор для сайтів на кшталт Telegram, які завжди повертають 200 OK."""
    @staticmethod
    def detect(status_code: int, response_data: Any, not_found_marker: str) -> Tuple[StatusEnum, ConfidenceLevel, Dict[str, Any]]:
        details = {}
        if status_code == 200 and isinstance(response_data, str):
            # Якщо в HTML-коді є маркер відсутності акаунта
            if not_found_marker.lower() in response_data.lower():
                return StatusEnum.NOT_FOUND, ConfidenceLevel.HIGH, details
            return StatusEnum.FOUND, ConfidenceLevel.HIGH, details
        elif status_code == 404:
            return StatusEnum.NOT_FOUND, ConfidenceLevel.HIGH, details
        elif status_code in (429, 403):
            return StatusEnum.RATE_LIMITED, ConfidenceLevel.LOW, details
        return StatusEnum.ERROR, ConfidenceLevel.LOW, details
