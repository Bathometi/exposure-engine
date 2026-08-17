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
