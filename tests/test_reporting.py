import json

from core.reporting import save_json_report
from core.schema import (
    ConfidenceLevel,
    EntityType,
    Evidence,
    StatusEnum,
)


def test_save_json_report(tmp_path):
    evidence = Evidence(
        entity_type=EntityType.USERNAME,
        raw_value="@Octocat",
        normalized_value="octocat",
        source_name="GitHub",
        status=StatusEnum.FOUND,
        confidence=ConfidenceLevel.HIGH,
        details={
            "target_url": "https://api.github.com/users/octocat",
            "http_status": 200,
            "name": "The Octocat",
        },
    )

    output_path = save_json_report(
        entity_type=EntityType.USERNAME,
        raw_value="@Octocat",
        normalized_value="octocat",
        evidences=[evidence],
        reports_dir=str(tmp_path),
    )

    assert output_path.exists()
    assert output_path.suffix == ".json"
    assert "username_octocat" in output_path.name

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    assert report["scan"]["entity_type"] == "username"
    assert report["scan"]["raw_value"] == "@Octocat"
    assert report["scan"]["normalized_value"] == "octocat"
    assert report["scan"]["results_count"] == 1

    assert len(report["results"]) == 1

    result = report["results"][0]

    assert result["source_name"] == "GitHub"
    assert result["status"] == "found"
    assert result["confidence"] == "high"
    assert result["details"]["http_status"] == 200



def test_save_json_report_with_enrichments(tmp_path):
    enrichments = {
        "dns": {
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
    }

    output_path = save_json_report(
        entity_type=EntityType.EMAIL,
        raw_value="user@example.com",
        normalized_value="user@example.com",
        evidences=[],
        enrichments=enrichments,
        reports_dir=str(tmp_path),
    )

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    assert report["enrichments"] == enrichments
def test_save_json_report_with_analysis(tmp_path):
    analysis = {
        "email_exposure_summary": {
            "checked_source_count": 4,
            "public_trace_count": 1,
            "found_sources": ["GitHub Commits"],
            "not_found_sources": [
                "Gravatar",
                "OpenPGP",
            ],
            "unavailable_sources": ["HIBP"],
            "uncertain_sources": [],
        }
    }

    output_path = save_json_report(
        entity_type=EntityType.EMAIL,
        raw_value="user@example.com",
        normalized_value="user@example.com",
        evidences=[],
        analysis=analysis,
        reports_dir=str(tmp_path),
    )

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    assert report["analysis"] == analysis
