import pytest

import check_username


@pytest.mark.parametrize(
    "raw_username",
    [
        "",
        "john doe",
        "a" * 129,
    ],
)
@pytest.mark.asyncio
async def test_invalid_username_stops_before_http_and_report(
    monkeypatch,
    raw_username,
):
    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "HTTP or report generation must not run "
            "for an invalid username."
        )

    monkeypatch.setattr(
        check_username,
        "HTTPCollector",
        fail_if_called,
    )

    monkeypatch.setattr(
        check_username,
        "save_json_report",
        fail_if_called,
    )

    result = await check_username.scan_username(
        raw_username
    )

    assert result is False
@pytest.mark.asyncio
async def test_username_cli_shows_youtube_channel_details(
    monkeypatch,
):
    from io import StringIO

    from rich.console import Console

    from core.schema import (
        ConfidenceLevel,
        EntityType,
        Evidence,
        StatusEnum,
    )

    class FakeCollector:
        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            return False

        async def check_platform(
            self,
            source_name,
            **kwargs,
        ):
            return Evidence(
                entity_type=EntityType.USERNAME,
                raw_value="@somehandle",
                normalized_value="somehandle",
                source_name=source_name,
                status=StatusEnum.FOUND,
                confidence=ConfidenceLevel.HIGH,
                details={
                    "http_status": 200,
                    "target_url": (
                        "https://www.googleapis.com/"
                        "youtube/v3/channels"
                    ),
                    "channel_id": "UC123456",
                    "title": "Example Channel",
                    "custom_url": "@somehandle",
                    "published_at": "2020-01-02T03:04:05Z",
                    "subscriber_count": "56",
                    "video_count": "7",
                    "view_count": "1234",
                },
                limitations=(
                    "Status determined via youtube detector."
                ),
            )

    output = StringIO()

    monkeypatch.setattr(
        check_username,
        "console",
        Console(
            file=output,
            force_terminal=False,
            width=200,
        ),
    )

    monkeypatch.setattr(
        check_username,
        "HTTPCollector",
        FakeCollector,
    )

    monkeypatch.setattr(
        check_username,
        "PLATFORMS",
        {
            "YouTube": {
                "url_template": (
                    "https://www.googleapis.com/"
                    "youtube/v3/channels"
                ),
                "detector": "youtube",
            },
        },
    )

    monkeypatch.setattr(
        check_username,
        "save_json_report",
        lambda **kwargs: "report.json",
    )

    result = await check_username.scan_username(
        "@somehandle"
    )

    rendered = output.getvalue()

    assert result is True
    assert "Channel ID" in rendered
    assert "UC123456" in rendered
    assert "Title" in rendered
    assert "Example Channel" in rendered
    assert "Handle" in rendered
    assert "@somehandle" in rendered
    assert "Published At" in rendered
    assert "2020-01-02 03:04:05 UTC" in rendered
    assert "Subscribers" in rendered
    assert "56" in rendered
    assert "Videos" in rendered
    assert "7" in rendered
    assert "Views" in rendered
    assert "1234" in rendered
