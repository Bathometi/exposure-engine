import asyncio
import aiohttp
from typing import Dict, Any

from core.schema import (
    Evidence,
    EntityType,
    StatusEnum,
    ConfidenceLevel,
)
from core.detector_registry import DETECTOR_REGISTRY


class HTTPCollector:
    def __init__(
        self,
        timeout_seconds: int = 5,
        max_retries: int = 3,
    ):
        self.timeout = aiohttp.ClientTimeout(
            total=timeout_seconds
        )

        self.max_retries = max_retries

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "OSINT-Exposure-Engine/1.0"
            )
        }

    async def check_platform(
        self,
        entity_type: EntityType,
        raw_value: str,
        normalized_value: str,
        source_name: str,
        platform_config: Dict[str, Any],
    ) -> Evidence:

        url = platform_config["url_template"].format(
            username=normalized_value
        )

        detector_name = platform_config.get(
            "detector",
            "status_code",
        )

        detector_config = DETECTOR_REGISTRY.get(
            detector_name
        )

        if detector_config is None:
            return Evidence(
                entity_type=entity_type,
                raw_value=raw_value,
                normalized_value=normalized_value,
                source_name=source_name,
                status=StatusEnum.ERROR,
                confidence=ConfidenceLevel.LOW,
                details={
                    "error": (
                        f"Unknown detector: "
                        f"{detector_name}"
                    ),
                    "target_url": url,
                },
                limitations=(
                    "Detector is not registered."
                ),
            )

        detector = detector_config["detector"]

        response_type = detector_config[
            "response_type"
        ]

        for attempt in range(
            self.max_retries + 1
        ):
            try:
                async with aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=self.timeout,
                ) as session:

                    async with session.get(
                        url,
                        allow_redirects=True,
                    ) as response:

                        status_code = response.status

                        retryable_statuses = (
                            429,
                            500,
                            502,
                            503,
                            504,
                        )

                        server_error_statuses = (
                            500,
                            502,
                            503,
                            504,
                        )

                        if (
                            status_code
                            in retryable_statuses
                            and attempt
                            < self.max_retries
                        ):
                            delay = 2 ** (
                                attempt + 1
                            )

                            await asyncio.sleep(
                                delay
                            )

                            continue

                        if (
                            status_code
                            in server_error_statuses
                            and attempt
                            == self.max_retries
                        ):
                            return Evidence(
                                entity_type=entity_type,
                                raw_value=raw_value,
                                normalized_value=(
                                    normalized_value
                                ),
                                source_name=source_name,
                                status=StatusEnum.ERROR,
                                confidence=(
                                    ConfidenceLevel.LOW
                                ),
                                details={
                                    "error": (
                                        "Server error "
                                        "after retries"
                                    ),
                                    "target_url": url,
                                    "http_status": (
                                        status_code
                                    ),
                                },
                                limitations=(
                                    "Maximum retries "
                                    "exhausted."
                                ),
                            )

                        if response_type == "text":
                            response_data = (
                                await response.text()
                            )

                        elif response_type == "json":
                            try:
                                response_data = (
                                    await response.json()
                                )
                            except Exception:
                                response_data = None

                        else:
                            return Evidence(
                                entity_type=entity_type,
                                raw_value=raw_value,
                                normalized_value=(
                                    normalized_value
                                ),
                                source_name=source_name,
                                status=StatusEnum.ERROR,
                                confidence=(
                                    ConfidenceLevel.LOW
                                ),
                                details={
                                    "error": (
                                        "Unsupported "
                                        "response type: "
                                        f"{response_type}"
                                    ),
                                    "target_url": url,
                                    "http_status": (
                                        status_code
                                    ),
                                },
                                limitations=(
                                    "Invalid detector "
                                    "configuration."
                                ),
                            )

                        (
                            status,
                            confidence,
                            parsed_details,
                        ) = detector.detect(
                            status_code,
                            response_data,
                        )

                        parsed_details[
                            "target_url"
                        ] = url

                        parsed_details[
                            "http_status"
                        ] = status_code

                        return Evidence(
                            entity_type=entity_type,
                            raw_value=raw_value,
                            normalized_value=(
                                normalized_value
                            ),
                            source_name=source_name,
                            status=status,
                            confidence=confidence,
                            details=parsed_details,
                            limitations=(
                                "Status determined via "
                                f"{detector_name} "
                                "detector."
                            ),
                        )

            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    delay = 2 ** (
                        attempt + 1
                    )

                    await asyncio.sleep(delay)

                    continue

                return Evidence(
                    entity_type=entity_type,
                    raw_value=raw_value,
                    normalized_value=(
                        normalized_value
                    ),
                    source_name=source_name,
                    status=StatusEnum.ERROR,
                    confidence=ConfidenceLevel.LOW,
                    details={
                        "error": (
                            "Request timed out"
                        ),
                        "target_url": url,
                    },
                    limitations=(
                        "Timeout reached."
                    ),
                )

            except Exception as e:
                return Evidence(
                    entity_type=entity_type,
                    raw_value=raw_value,
                    normalized_value=(
                        normalized_value
                    ),
                    source_name=source_name,
                    status=StatusEnum.ERROR,
                    confidence=ConfidenceLevel.LOW,
                    details={
                        "error": str(e),
                        "target_url": url,
                    },
                    limitations=(
                        "Network failure."
                    ),
                )
