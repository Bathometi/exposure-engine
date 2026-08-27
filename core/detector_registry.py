from core.detectors import (
    ChessComDetector,
    CodebergDetector,
    DevToDetector,
    HackerNewsDetector,
    GravatarDetector,
    HIBPDetector,
    GitHubCommitDetector,
    OpenPGPDetector,
    HuggingFaceDetector,
    KeybaseDetector,
    LichessDetector,
    StatusCodeDetector,
    TelegramDetector,
    YouTubeDetector,
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

    "gravatar": {
        "detector": GravatarDetector,
        "response_type": "json",
    },
    "hibp": {
        "detector": HIBPDetector,
        "response_type": "json",
    },

    "github_commits": {
        "detector": GitHubCommitDetector,
        "response_type": "json",
    },
    "openpgp": {
        "detector": OpenPGPDetector,
        "response_type": "text",
    },

    "youtube": {
        "detector": YouTubeDetector,
        "response_type": "json",
    },
}
