from core.detectors import (
    CodebergDetector,
    DevToDetector,
    HackerNewsDetector,
    KeybaseDetector,
    LichessDetector,
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

    "codeberg": {
        "detector": CodebergDetector,
        "response_type": "json",
    },

    "keybase": {
        "detector": KeybaseDetector,
        "response_type": "json",
    },

    "lichess": {
        "detector": LichessDetector,
        "response_type": "json",
    },
}
