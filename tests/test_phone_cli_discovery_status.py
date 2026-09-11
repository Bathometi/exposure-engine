from unittest.mock import AsyncMock

import phonenumbers
import pytest

import check_phone


@pytest.mark.asyncio
async def test_phone_cli_preserves_partial_discovery(
    monkeypatch,
    capsys,
):
    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )
    target = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )

    mention = {
        "source": "GitHub",
        "repository": "example/repo",
        "path": "README.md",
        "url": "https://github.com/example/repo",
        "matched_variants": ["TEST_VARIANT_A"],
    }

    discovery = {
        "status": "partial",
        "mentions": [mention],
        "searches": [
            {
                "variant": "TEST_VARIANT_A",
                "status": "ok",
                "error": None,
            },
            {
                "variant": "TEST_VARIANT_B",
                "status": "unavailable",
                "error": "HTTP 503",
            },
        ],
    }

    class FakeCollector:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

    verify = AsyncMock(return_value=[])
    saved = {}

    def fake_save_json_report(**kwargs):
        saved.update(kwargs)
        return "TEST_REPORT"

    monkeypatch.setattr(
        check_phone, "HTTPCollector", FakeCollector
    )
    monkeypatch.setattr(
        check_phone,
        "discover_phone_github_mentions",
        AsyncMock(return_value=discovery),
    )
    monkeypatch.setattr(
        check_phone, "verify_github_mentions", verify
    )
    monkeypatch.setattr(
        check_phone,
        "save_json_report",
        fake_save_json_report,
    )

    result = await check_phone.scan_phone(target)

    assert result is True
    verify.assert_awaited_once()
    assert verify.await_args.args[1] == [mention]

    analysis = saved["analysis"]["github_phone_mentions"]
    assert analysis["status"] == "partial"
    assert analysis["searches"] == discovery["searches"]
    assert analysis["results"] == []

    output = capsys.readouterr().out
    assert "Discovery status: partial" in output
    assert "Searches unavailable: 1" in output
