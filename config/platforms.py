PLATFORMS = {
    "GitHub": {
        "url_template": "https://api.github.com/users/{username}",
        "detector": "status_code",
    },

    "GitLab": {
        "url_template": (
            "https://gitlab.com/api/v4/users"
            "?username={username}"
        ),
        "detector": "status_code",
    },

    "DockerHub": {
        "url_template": (
            "https://hub.docker.com/v2/users/{username}"
        ),
        "detector": "status_code",
    },

    "Reddit": {
        "url_template": (
            "https://www.reddit.com/user/"
            "{username}/about.json"
        ),
        "detector": "status_code",
    },

    "Telegram": {
        "url_template": "https://t.me/{username}",
        "detector": "telegram",
    },

    "HackerNews": {
        "url_template": (
            "https://hacker-news.firebaseio.com/"
            "v0/user/{username}.json"
        ),
        "detector": "hackernews",
    },

    "DevTo": {
        "url_template": (
            "https://dev.to/api/users/"
            "by_username?url={username}"
        ),
        "detector": "devto",
    },

    "Codeberg": {
        "url_template": (
            "https://codeberg.org/api/v1/users/{username}"
        ),
        "detector": "codeberg",
    },

    "Keybase": {
        "url_template": (
            "https://keybase.io/_/api/1.0/"
            "user/lookup.json"
            "?username={username}"
            "&fields=basics,profile"
        ),
        "detector": "keybase",
    },

    "Lichess": {
        "url_template": (
            "https://lichess.org/api/user/{username}"
        ),
        "detector": "lichess",
    },

    "HuggingFace": {
        "url_template": (
            "https://huggingface.co/api/users/"
            "{username}/overview"
        ),
        "detector": "huggingface",
    },

    "ChessCom": {
        "url_template": (
            "https://api.chess.com/pub/player/{username}"
        ),
        "detector": "chesscom",
    },
}
