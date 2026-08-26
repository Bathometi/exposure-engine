import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

import aiohttp

from core.detector_registry import DETECTOR_REGISTRY
from core.identifiers import IDENTIFIER_REGISTRY
from core.schema import (
    ConfidenceLevel,
    EntityType,
    Evidence,
    StatusEnum,
)


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

        # Shared session.
        # Поки Collector не відкритий через async with,
        # тут зберігається None.
        self.session = None

    async def __aenter__(self):
        """
        Відкриває одну shared ClientSession
        для всього життєвого циклу Collector.
        """

        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout,
        )

        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        """
        Гарантовано закриває shared session
        після завершення роботи Collector.
        """

        if self.session is not None:
            await self.session.close()
            self.session = None

    @asynccontextmanager
    async def _session_scope(self):
        """
        Якщо shared session вже відкрита —
        використовуємо її.

        Якщо Collector викликаний старим способом
        без async with — тимчасово створюємо session.
        """

        if self.session is not None:
            yield self.session
            return

        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout,
        ) as session:
            yield session
    def _resolve_request_headers(
        self,
        platform_config: Dict[str, Any],
    ) -> Dict[str, str]:
        headers = {}

        for header_name, env_name in (
            platform_config.get(
                "headers_from_env",
                {},
            ).items()
        ):
            value = os.getenv(env_name)

            if value:
                headers[header_name] = value

        return headers

    def _resolve_query_params(
        self,
        platform_config: Dict[str, Any],
        request_value: str,
    ) -> Dict[str, Any]:
        params = {}

        for param_name, template in (
            platform_config.get(
                "query_params",
                {},
            ).items()
        ):
            if isinstance(template, str):
                params[param_name] = template.format(
                    username=request_value,
                    value=request_value,
                )
            else:
                params[param_name] = template

        for param_name, env_name in (
            platform_config.get(
                "query_params_from_env",
                {},
            ).items()
        ):
            value = os.getenv(env_name)

            if value:
                params[param_name] = value

        return params

    async def check_platform(
        self,
        entity_type: EntityType,
        raw_value: str,
        normalized_value: str,
        source_name: str,
        platform_config: Dict[str, Any],
    ) -> Evidence:

        identifier_name = platform_config.get(
            "identifier",
            "identity",
        )

        identifier = IDENTIFIER_REGISTRY[
            identifier_name
        ]

        request_value = identifier(
            normalized_value
        )

        url = platform_config["url_template"].format(
            username=request_value,
            value=request_value,
        )
        request_headers = self._resolve_request_headers(
            platform_config
        )

        request_params = self._resolve_query_params(
            platform_config,
            request_value,
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
                async with self._session_scope() as session:

                    async with session.get(
                        url,
                        headers=request_headers,
                        params=request_params,
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
