import pytest

import check_phone


@pytest.fixture(autouse=True)
def prevent_live_github_calls(monkeypatch):
    class FakeCollector:
        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            return None

    async def fake_discover(
        collector,
        phone,
    ):
        return []

    monkeypatch.setattr(
        check_phone,
        "HTTPCollector",
        FakeCollector,
    )

    monkeypatch.setattr(
        check_phone,
        "discover_phone_github_mentions",
        fake_discover,
    )


@pytest.mark.asyncio
async def test_invalid_phone_stops_before_http(
    monkeypatch,
):
    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "HTTP must not run for an invalid phone."
        )

    monkeypatch.setattr(
        check_phone,
        "HTTPCollector",
        fail_if_called,
    )

    result = await check_phone.scan_phone(
        "TEST_PHONE"
    )

    assert result is False


@pytest.mark.asyncio
async def test_valid_phone_collects_local_intelligence(
    monkeypatch,
):
    import phonenumbers

    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )

    target = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )

    received = []

    def fake_collect_phone_intelligence(value):
        received.append(value)

        return {
            "possible": True,
            "valid": True,
            "region": "GB",
            "location": "",
            "carrier": "",
            "type": "mobile",
            "timezones": [],
        }

    monkeypatch.setattr(
        check_phone,
        "collect_phone_intelligence",
        fake_collect_phone_intelligence,
    )

    result = await check_phone.scan_phone(target)

    assert result is True
    assert received == [target]


@pytest.mark.asyncio
async def test_valid_phone_shows_local_intelligence(
    monkeypatch,
    capsys,
):
    import phonenumbers

    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )

    target = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )

    monkeypatch.setattr(
        check_phone,
        "collect_phone_intelligence",
        lambda value: {
            "possible": True,
            "valid": True,
            "region": "GB",
            "location": "United Kingdom",
            "carrier": "Test Carrier",
            "type": "mobile",
            "timezones": ["Europe/London"],
        },
    )

    result = await check_phone.scan_phone(target)

    output = capsys.readouterr().out

    assert result is True
    assert "PHONE INTELLIGENCE" in output
    assert "Possible: True" in output
    assert "Valid: True" in output
    assert "Region: GB" in output
    assert "Type: mobile" in output


@pytest.mark.asyncio
async def test_valid_phone_discovers_github_mentions(
    monkeypatch,
):
    import phonenumbers

    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )

    target = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )

    monkeypatch.setattr(
        check_phone,
        "collect_phone_intelligence",
        lambda value: {
            "possible": True,
            "valid": True,
            "region": "GB",
            "location": "",
            "carrier": "",
            "type": "mobile",
            "timezones": [],
        },
    )

    received = []

    async def fake_discover(
        collector,
        phone,
    ):
        received.append(phone)
        return []

    monkeypatch.setattr(
        check_phone,
        "discover_phone_github_mentions",
        fake_discover,
    )

    class FakeCollector:
        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            return None

    monkeypatch.setattr(
        check_phone,
        "HTTPCollector",
        FakeCollector,
    )

    result = await check_phone.scan_phone(target)

    assert result is True
    assert received == [target]


@pytest.mark.asyncio
async def test_valid_phone_verifies_github_mentions(
    monkeypatch,
):
    import phonenumbers

    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )

    target = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )

    monkeypatch.setattr(
        check_phone,
        "collect_phone_intelligence",
        lambda value: {
            "possible": True,
            "valid": True,
            "region": "GB",
            "location": "",
            "carrier": "",
            "type": "mobile",
            "timezones": [],
        },
    )

    mentions = [
        {
            "source": "GitHub",
            "repository": "example/repo",
            "path": "contacts.txt",
            "url": "https://github.com/example/repo",
            "api_url": "https://api.github.com/example/file",
            "matched_variant": "TEST_VARIANT",
        }
    ]

    async def fake_discover(
        collector,
        phone,
    ):
        return mentions

    received = []

    async def fake_verify(
        collector,
        candidates,
    ):
        received.extend(candidates)
        return []

    monkeypatch.setattr(
        check_phone,
        "discover_phone_github_mentions",
        fake_discover,
    )

    monkeypatch.setattr(
        check_phone,
        "verify_github_mentions",
        fake_verify,
    )

    result = await check_phone.scan_phone(target)

    assert result is True
    assert received == mentions


@pytest.mark.asyncio
async def test_valid_phone_summarizes_github_verifications(
    monkeypatch,
):
    import phonenumbers

    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )

    target = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )

    monkeypatch.setattr(
        check_phone,
        "collect_phone_intelligence",
        lambda value: {
            "possible": True,
            "valid": True,
            "region": "GB",
            "location": "",
            "carrier": "",
            "type": "mobile",
            "timezones": [],
        },
    )

    async def fake_discover(
        collector,
        phone,
    ):
        return [
            {
                "source": "GitHub",
                "repository": "example/repo",
                "path": "contacts.txt",
                "url": "https://github.com/example/repo",
                "api_url": "https://api.github.com/example/file",
                "matched_variant": "TEST_VARIANT",
            }
        ]

    verified = [
        {
            "verification": {
                "status": "verified",
                "classification": "phone_context",
            }
        }
    ]

    async def fake_verify(
        collector,
        mentions,
    ):
        return verified

    received = []

    def fake_summarize(results):
        received.extend(results)

        return {
            "candidate_count": 1,
            "verified_string_occurrences": 1,
            "phone_context": 1,
            "example_or_test_data": 0,
            "numeric_noise": 0,
            "uncertain": 0,
            "not_verified": 0,
            "unavailable": 0,
        }

    monkeypatch.setattr(
        check_phone,
        "discover_phone_github_mentions",
        fake_discover,
    )

    monkeypatch.setattr(
        check_phone,
        "verify_github_mentions",
        fake_verify,
    )

    monkeypatch.setattr(
        check_phone,
        "summarize_github_verifications",
        fake_summarize,
    )

    result = await check_phone.scan_phone(target)

    assert result is True
    assert received == verified


@pytest.mark.asyncio
async def test_valid_phone_shows_github_summary(
    monkeypatch,
    capsys,
):
    import phonenumbers

    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )

    target = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )

    monkeypatch.setattr(
        check_phone,
        "collect_phone_intelligence",
        lambda value: {
            "possible": True,
            "valid": True,
            "region": "GB",
            "location": "",
            "carrier": "",
            "type": "mobile",
            "timezones": [],
        },
    )

    async def fake_verify(
        collector,
        mentions,
    ):
        return []

    monkeypatch.setattr(
        check_phone,
        "verify_github_mentions",
        fake_verify,
    )

    monkeypatch.setattr(
        check_phone,
        "summarize_github_verifications",
        lambda results: {
            "candidate_count": 3,
            "verified_string_occurrences": 1,
            "phone_context": 1,
            "example_or_test_data": 1,
            "numeric_noise": 0,
            "uncertain": 0,
            "not_verified": 1,
            "unavailable": 0,
        },
    )

    result = await check_phone.scan_phone(target)

    output = capsys.readouterr().out

    assert result is True
    assert "GITHUB PHONE MENTIONS" in output
    assert "Candidates: 3" in output
    assert "Verified string occurrences: 1" in output
    assert "Phone context: 1" in output
    assert "Example/test data: 1" in output
    assert "Not verified: 1" in output


@pytest.mark.asyncio
async def test_valid_phone_saves_structured_report(
    monkeypatch,
):
    import phonenumbers

    from core.schema import EntityType

    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )

    target = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )

    intelligence = {
        "possible": True,
        "valid": True,
        "region": "GB",
        "location": "United Kingdom",
        "carrier": "",
        "type": "MOBILE",
        "timezones": ["Europe/London"],
    }

    verified = [
        {
            "source": "GitHub",
            "repository": "example/repo",
            "path": "contacts.txt",
            "verification": {
                "status": "verified",
                "classification": "phone_context",
            },
        }
    ]

    summary = {
        "candidate_count": 1,
        "verified_string_occurrences": 1,
        "phone_context": 1,
        "example_or_test_data": 0,
        "numeric_noise": 0,
        "uncertain": 0,
        "not_verified": 0,
        "unavailable": 0,
    }

    monkeypatch.setattr(
        check_phone,
        "collect_phone_intelligence",
        lambda value: intelligence,
    )

    async def fake_verify(
        collector,
        mentions,
    ):
        return verified

    monkeypatch.setattr(
        check_phone,
        "verify_github_mentions",
        fake_verify,
    )

    monkeypatch.setattr(
        check_phone,
        "summarize_github_verifications",
        lambda results: summary,
    )

    saved = {}

    def fake_save_json_report(**kwargs):
        saved.update(kwargs)
        return "report.json"

    monkeypatch.setattr(
        check_phone,
        "save_json_report",
        fake_save_json_report,
    )

    result = await check_phone.scan_phone(target)

    assert result is True
    assert saved["entity_type"] == EntityType.PHONE
    assert saved["raw_value"] == target
    assert saved["normalized_value"] == target
    assert saved["evidences"] == []

    assert saved["enrichments"] == {
        "phone_intelligence": intelligence,
    }

    assert saved["analysis"] == {
        "github_phone_mentions": {
            "summary": summary,
            "results": verified,
        }
    }
