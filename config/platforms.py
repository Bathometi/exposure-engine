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
}
