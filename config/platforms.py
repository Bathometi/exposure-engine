# Налаштування платформ та правил детеції
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
        "detector": "html_marker",
        "not_found_marker": "If you have Telegram, you can contact"  # Маркер, що акаунта немає / це приватна сторінка
    }
}
