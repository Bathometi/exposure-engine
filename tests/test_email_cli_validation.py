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



@pytest.mark.asyncio
async def test_email_scan_passes_dns_enrichment_to_report(monkeypatch):
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

    dns_result = {
        "domain": "example.com",
        "mx": [
            {
                "priority": 10,
                "host": "mail.example.com",
            }
        ],
        "spf": "v=spf1 -all",
        "dmarc": "v=DMARC1; p=reject",
    }

    saved_report = {}

    def fake_save_json_report(**kwargs):
        saved_report.update(kwargs)
        return "report.json"

    monkeypatch.setattr(
        check_email,
        "HTTPCollector",
        FakeCollector,
    )

    monkeypatch.setattr(
        check_email,
        "EMAIL_PLATFORMS",
        {},
    )

    monkeypatch.setattr(
        check_email,
        "collect_email_domain_intelligence",
        lambda email: dns_result,
    )

    monkeypatch.setattr(
        check_email,
        "save_json_report",
        fake_save_json_report,
    )

    result = await check_email.scan_email(
        "User@Example.COM"
    )

    assert result is True
    assert saved_report["normalized_value"] == "user@example.com"
    assert saved_report["enrichments"] == {
        "dns": dns_result
    }


@pytest.mark.asyncio
async def test_email_cli_shows_github_commit_details(
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
            **kwargs,
        ):
            return Evidence(
                entity_type=EntityType.EMAIL,
                raw_value="user@example.com",
                normalized_value="user@example.com",
                source_name="GitHub Commits",
                status=StatusEnum.FOUND,
                confidence=ConfidenceLevel.HIGH,
                details={
                    "http_status": 200,
                    "target_url": (
                        "https://api.github.com/search/commits"
                    ),
                    "commit_count": 71,
                    "linked_users": [
                        "example-user",
                    ],
                    "repositories": [
                        "example/repo-one",
                        "example/repo-two",
                    ],
                    "sample_commits": [
                        {
                            "repository": "example/repo-one",
                            "sha": "abc123def4567890",
                            "author_date": "2026-08-20T10:00:00Z",
                            "url": "https://github.com/example/repo-one/commit/abc123def4567890",
                        },
                    ],
                },
                limitations=(
                    "Status determined via "
                    "github_commits detector."
                ),
            )

    output = StringIO()

    monkeypatch.setattr(
        check_email,
        "console",
        Console(
            file=output,
            force_terminal=False,
            width=200,
        ),
    )

    monkeypatch.setattr(
        check_email,
        "HTTPCollector",
        FakeCollector,
    )

    monkeypatch.setattr(
        check_email,
        "EMAIL_PLATFORMS",
        {
            "GitHub Commits": {
                "detector": "github_commits",
            }
        },
    )

    monkeypatch.setattr(
        check_email,
        "collect_email_domain_intelligence",
        lambda email: {
            "domain": "example.com",
            "mx": [],
            "spf": None,
            "dmarc": None,
        },
    )

    monkeypatch.setattr(
        check_email,
        "save_json_report",
        lambda **kwargs: "report.json",
    )

    result = await check_email.scan_email(
        "user@example.com"
    )

    rendered = output.getvalue()

    assert result is True
    assert "Commit Count" in rendered
    assert "71" in rendered
    assert "Linked Users" in rendered
    assert "example-user" in rendered
    assert "Repositories" in rendered
    assert "example/repo-one" in rendered
    assert "example/repo-two" in rendered
    assert "Sample Commits" in rendered
    assert "abc123d • 2026-08-20 10:00 UTC" in rendered
    assert "2026-08-20T10:00:00Z" not in rendered
    assert "https://github.com/example/repo-one/commit/abc123def4567890" in rendered
    assert "EMAIL EXPOSURE SUMMARY" in rendered
    assert "Checked Sources" in rendered
    assert "Public Traces" in rendered


@pytest.mark.asyncio
async def test_email_cli_preserves_source_exception_as_error_evidence(
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
            if source_name == "HIBP":
                raise RuntimeError("temporary API failure")

            return Evidence(
                entity_type=EntityType.EMAIL,
                raw_value="user@example.com",
                normalized_value="user@example.com",
                source_name=source_name,
                status=StatusEnum.FOUND,
                confidence=ConfidenceLevel.HIGH,
            )

    output = StringIO()
    captured_report = {}

    monkeypatch.setattr(
        check_email,
        "console",
        Console(
            file=output,
            force_terminal=False,
            width=200,
        ),
    )

    monkeypatch.setattr(
        check_email,
        "HTTPCollector",
        FakeCollector,
    )

    monkeypatch.setattr(
        check_email,
        "EMAIL_PLATFORMS",
        {
            "GitHub Commits": {
                "detector": "github_commits",
            },
            "HIBP": {
                "detector": "hibp",
            },
        },
    )

    monkeypatch.setattr(
        check_email,
        "collect_email_domain_intelligence",
        lambda email: {
            "domain": "example.com",
            "mx": [],
            "spf": None,
            "dmarc": None,
        },
    )

    def fake_save_json_report(**kwargs):
        captured_report.update(kwargs)
        return "report.json"

    monkeypatch.setattr(
        check_email,
        "save_json_report",
        fake_save_json_report,
    )

    result = await check_email.scan_email(
        "user@example.com"
    )

    rendered = output.getvalue()
    evidences = captured_report["evidences"]

    assert result is True
    assert "Checked Sources" in rendered
    assert "2" in rendered
    assert "Unavailable" in rendered
    assert "HIBP" in rendered
    assert len(evidences) == 2

    hibp_evidence = next(
        evidence
        for evidence in evidences
        if evidence.source_name == "HIBP"
    )

    assert hibp_evidence.status == StatusEnum.ERROR
    assert hibp_evidence.confidence == ConfidenceLevel.LOW
