import pytest

import check_email


@pytest.mark.parametrize(
    "raw_email",
    [
        "",
        "user example@example.com",
        "userexample.com",
        "\udcd1user@example.com",
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



def test_main_scans_all_cli_email_arguments(monkeypatch):
    scanned_emails = []

    async def fake_scan_email(raw_email):
        scanned_emails.append(raw_email)
        return True

    monkeypatch.setattr(
        check_email,
        "scan_email",
        fake_scan_email,
    )

    monkeypatch.setattr(
        check_email.sys,
        "argv",
        [
            "check_email.py",
            "first@example.com",
            "second@example.com",
        ],
    )

    check_email.main()

    assert scanned_emails == [
        "first@example.com",
        "second@example.com",
    ]
