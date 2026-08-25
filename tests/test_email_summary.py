from core.email_summary import EmailExposureSummary
from core.schema import ConfidenceLevel, EntityType, Evidence, StatusEnum


def test_email_summary_counts_public_traces():
    results = [
        Evidence(
            entity_type=EntityType.EMAIL,
            raw_value="user@example.com",
            normalized_value="user@example.com",
            source_name="Gravatar",
            status=StatusEnum.NOT_FOUND,
            confidence=ConfidenceLevel.HIGH,
        ),
        Evidence(
            entity_type=EntityType.EMAIL,
            raw_value="user@example.com",
            normalized_value="user@example.com",
            source_name="GitHub Commits",
            status=StatusEnum.FOUND,
            confidence=ConfidenceLevel.HIGH,
        ),
        Evidence(
            entity_type=EntityType.EMAIL,
            raw_value="user@example.com",
            normalized_value="user@example.com",
            source_name="OpenPGP",
            status=StatusEnum.FOUND,
            confidence=ConfidenceLevel.HIGH,
        ),
        Evidence(
            entity_type=EntityType.EMAIL,
            raw_value="user@example.com",
            normalized_value="user@example.com",
            source_name="HIBP",
            status=StatusEnum.ERROR,
            confidence=ConfidenceLevel.LOW,
        ),
    ]

    summary = EmailExposureSummary.build(results)

    assert summary["public_trace_count"] == 2
    assert summary["checked_source_count"] == 4
    assert summary["found_sources"] == [
        "GitHub Commits",
        "OpenPGP",
    ]
    assert summary["unavailable_sources"] == [
        "HIBP",
    ]
    assert summary["not_found_sources"] == [
        "Gravatar",
    ]



def test_marks_rate_limited_source_as_unavailable():
    results = [
        Evidence(
            entity_type=EntityType.EMAIL,
            raw_value="user@example.com",
            normalized_value="user@example.com",
            source_name="OpenPGP",
            status=StatusEnum.RATE_LIMITED,
            confidence=ConfidenceLevel.MEDIUM,
        ),
    ]

    summary = EmailExposureSummary.build(results)

    assert summary["unavailable_sources"] == ["OpenPGP"]



def test_marks_blocked_source_as_unavailable():
    results = [
        Evidence(
            entity_type=EntityType.EMAIL,
            raw_value="user@example.com",
            normalized_value="user@example.com",
            source_name="Gravatar",
            status=StatusEnum.BLOCKED,
            confidence=ConfidenceLevel.MEDIUM,
       ),
    ]

    summary = EmailExposureSummary.build(results)

    assert summary["unavailable_sources"] == ["Gravatar"]



def test_marks_unknown_source_as_uncertain():
    results = [
        Evidence(
            entity_type=EntityType.EMAIL,
            raw_value="user@example.com",
            normalized_value="user@example.com",
            source_name="OpenPGP",
            status=StatusEnum.UNKNOWN,
            confidence=ConfidenceLevel.LOW,
        ),
    ]

    summary = EmailExposureSummary.build(results)

    assert summary["uncertain_sources"] == ["OpenPGP"]
