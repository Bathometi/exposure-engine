from config.platforms import PLATFORMS


def test_all_platforms_have_url_template():
    for platform_name, config in PLATFORMS.items():
        assert "url_template" in config, (
            f"{platform_name} has no url_template"
        )

        has_placeholder = (
            "{username}" in config["url_template"]
            or any(
                isinstance(value, str)
                and (
                    "{username}" in value
                    or "{value}" in value
                )
                for value in config.get(
                    "query_params",
                    {},
                ).values()
            )
        )

        assert has_placeholder, (
            f"{platform_name} has no request-value placeholder"
        )


def test_all_platforms_have_supported_detector():
    supported_detectors = {
        "status_code",
        "telegram",
        "hackernews",
        "devto",
        "codeberg",
        "keybase",
        "lichess",
        "huggingface",
        "chesscom",
        "youtube",
    }

    for platform_name, config in PLATFORMS.items():
        assert config.get("detector") in supported_detectors, (
            f"{platform_name} uses unsupported detector"
        )


def test_telegram_uses_telegram_detector():
    assert (
        PLATFORMS["Telegram"]["detector"]
        == "telegram"
    )


def test_hackernews_uses_hackernews_detector():
    assert (
        PLATFORMS["HackerNews"]["detector"]
        == "hackernews"
    )


def test_hackernews_has_username_placeholder():
    assert (
        "{username}"
        in PLATFORMS["HackerNews"]["url_template"]
    )


def test_devto_uses_devto_detector():
    assert (
        PLATFORMS["DevTo"]["detector"]
        == "devto"
    )


def test_devto_has_username_placeholder():
    assert (
        "{username}"
        in PLATFORMS["DevTo"]["url_template"]
    )


def test_codeberg_uses_codeberg_detector():
    assert (
        PLATFORMS["Codeberg"]["detector"]
        == "codeberg"
    )


def test_codeberg_has_username_placeholder():
    assert (
        "{username}"
        in PLATFORMS["Codeberg"]["url_template"]
    )


def test_keybase_uses_keybase_detector():
    assert (
        PLATFORMS["Keybase"]["detector"]
        == "keybase"
    )


def test_keybase_has_username_placeholder():
    assert (
        "{username}"
        in PLATFORMS["Keybase"]["url_template"]
    )


def test_lichess_uses_lichess_detector():
    assert (
        PLATFORMS["Lichess"]["detector"]
        == "lichess"
    )


def test_lichess_has_username_placeholder():
    assert (
        "{username}"
        in PLATFORMS["Lichess"]["url_template"]
    )


def test_huggingface_uses_huggingface_detector():
    assert (
        PLATFORMS["HuggingFace"]["detector"]
        == "huggingface"
    )


def test_huggingface_has_username_placeholder():
    assert (
        "{username}"
        in PLATFORMS["HuggingFace"]["url_template"]
    )


def test_chesscom_uses_chesscom_detector():
    assert (
        PLATFORMS["ChessCom"]["detector"]
        == "chesscom"
    )


def test_chesscom_has_username_placeholder():
    assert (
        "{username}"
        in PLATFORMS["ChessCom"]["url_template"]
    )
def test_youtube_source_is_configured():
    config = PLATFORMS["YouTube"]

    assert config["url_template"] == (
        "https://www.googleapis.com/youtube/v3/channels"
    )
    assert config["detector"] == "youtube"
    assert config["query_params"] == {
        "part": "snippet,statistics",
        "forHandle": "{value}",
    }
    assert config["query_params_from_env"] == {
        "key": "YOUTUBE_API_KEY",
    }
