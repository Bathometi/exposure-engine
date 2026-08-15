from core.detectors import (
    DevToDetector,
    HackerNewsDetector,
    StatusCodeDetector,
    TelegramDetector,
)


DETECTOR_REGISTRY = {
    "status_code": {
        "detector": StatusCodeDetector,
        "response_type": "json",
    },

    "telegram": {
        "detector": TelegramDetector,
        "response_type": "text",
    },

    "hackernews": {
        "detector": HackerNewsDetector,
        "response_type": "json",
    },

    "devto": {
        "detector": DevToDetector,
        "response_type": "json",
    },
}
