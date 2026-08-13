from config.platforms import PLATFORMS


def test_all_platforms_have_url_template():
    for platform_name, config in PLATFORMS.items():
        assert "url_template" in config, (
            f"{platform_name} has no url_template"
        )

        assert "{username}" in config["url_template"], (
            f"{platform_name} url_template has no {{username}} placeholder"
        )


def test_all_platforms_have_supported_detector():
    supported_detectors = {"status_code", "telegram"}

    for platform_name, config in PLATFORMS.items():
        assert config.get("detector") in supported_detectors, (
            f"{platform_name} uses unsupported detector"
        )


def test_telegram_uses_telegram_detector():
    assert PLATFORMS["Telegram"]["detector"] == "telegram"
