import asyncio
import aiohttp
from typing import Optional
from core.schema import Evidence, EntityType, StatusEnum, ConfidenceLevel


class HTTPCollector:
    def __init__(self, timeout_seconds: int = 5, max_retries: int = 2):
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OSINT-Exposure-Engine/1.0"
        }

    async def check_url(
        self, 
        entity_type: EntityType, 
        raw_value: str, 
        normalized_value: str, 
        url: str, 
        source_name: str
    ) -> Evidence:
        """Асинхронний HTTP GET запит із підтримкою retries та exponential backoff."""
        
        for attempt in range(1, self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
                    async with session.get(url, allow_redirects=True) as response:
                        status_code = response.status

                        # Якщо середовище просить почекати (429) або сервер тимчасово впав (50x)
                        if status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                            backoff_time = 2 ** attempt  # 2сек, 4сек...
                            print(f"[!] {source_name} returned {status_code}. Retrying in {backoff_time}s (Attempt {attempt}/{self.max_retries})...")
                            await asyncio.sleep(backoff_time)
                            continue

                        if status_code == 200:
                            status = StatusEnum.FOUND
                            confidence = ConfidenceLevel.HIGH
                        elif status_code == 404:
                            status = StatusEnum.NOT_FOUND
                            confidence = ConfidenceLevel.HIGH
                        elif status_code in (429, 403):
                            status = StatusEnum.RATE_LIMITED
                            confidence = ConfidenceLevel.LOW
                        else:
                            status = StatusEnum.ERROR
                            confidence = ConfidenceLevel.LOW

                        return Evidence(
                            entity_type=entity_type,
                            raw_value=raw_value,
                            normalized_value=normalized_value,
                            source_name=source_name,
                            status=status,
                            confidence=confidence,
                            details={"http_status": status_code, "target_url": url, "attempts": attempt},
                            limitations="Status determined via HTTP response status code."
                        )

            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    backoff_time = 2 ** attempt
                    print(f"[!] Timeout on {source_name}. Retrying in {backoff_time}s (Attempt {attempt}/{self.max_retries})...")
                    await asyncio.sleep(backoff_time)
                    continue

                return Evidence(
                    entity_type=entity_type,
                    raw_value=raw_value,
                    normalized_value=normalized_value,
                    source_name=source_name,
                    status=StatusEnum.ERROR,
                    confidence=ConfidenceLevel.LOW,
                    details={"error": "Request timed out after retries", "attempts": attempt},
                    limitations="Target server failed to respond within timeout window."
                )
            except Exception as e:
                return Evidence(
                    entity_type=entity_type,
                    raw_value=raw_value,
                    normalized_value=normalized_value,
                    source_name=source_name,
                    status=StatusEnum.ERROR,
                    confidence=ConfidenceLevel.LOW,
                    details={"error": str(e), "attempts": attempt},
                    limitations="Network or connection level failure occurred."
                )
