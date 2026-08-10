PLATFORMS = {
    "GitHub": {
        "url_template": "https://api.github.com/users/{username}",
        "detector": "status_code",
    },
    "DockerHub": {
        "url_template": "https://hub.docker.com/v2/users/{username}",
        "detector": "status_code",
    },
    "Telegram": {
        "url_template": "https://t.me/{username}",
        "detector": "telegram",
    }
}
