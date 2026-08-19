from core.detectors import (
    ChessComDetector,
    CodebergDetector,
    DevToDetector,
    HackerNewsDetector,
    HuggingFaceDetector,
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

    "huggingface": {
        "detector": HuggingFaceDetector,
        "response_type": "json",
    },

    "chesscom": {
        "detector": ChessComDetector,
        "response_type": "json",
    },
}
