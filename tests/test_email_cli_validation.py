import pytest

import check_email


@pytest.mark.parametrize(
    "raw_email",
    [
        "",
        "user example@example.com",
        "userexample.com",
    ],
)
@pytest.mark.asyncio
async def test_invalid_email_stops_before_http_and_report(
    monkeypatch,
    raw_email,
):
    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "HTTP or report generation must not run "
            "for an invalid email."
        )

    monkeypatch.setattr(
        check_email,
        "HTTPCollector",
        fail_if_called,
    )

    monkeypatch.setattr(
        check_email,
        "save_json_report",
        fail_if_called,
    )

    result = await check_email.scan_email(
        raw_email
    )

    assert result is False
