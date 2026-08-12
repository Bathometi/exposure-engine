import pytest
from pydantic import ValidationError

from core.schema import (
    Evidence,
    EntityType,
    StatusEnum,
    ConfidenceLevel,
)


def test_valid_evidence():
    evidence = Evidence(
        entity_type=EntityType.USERNAME,
        raw_value=" @Octocat ",
        normalized_value="octocat",
        source_name="GitHub",
        status=StatusEnum.FOUND,
        confidence=ConfidenceLevel.HIGH,
    )

    assert evidence.entity_type == EntityType.USERNAME
    assert evidence.normalized_value == "octocat"
    assert evidence.status == StatusEnum.FOUND
    assert evidence.confidence == ConfidenceLevel.HIGH


def test_evidence_default_values():
    evidence = Evidence(
        entity_type=EntityType.USERNAME,
        raw_value="test",
        normalized_value="test",
        source_name="GitHub",
        status=StatusEnum.UNKNOWN,
        confidence=ConfidenceLevel.LOW,
    )

    assert evidence.details == {}
    assert evidence.limitations is None


def test_invalid_status_is_rejected():
    with pytest.raises(ValidationError):
        Evidence(
            entity_type=EntityType.USERNAME,
            raw_value="test",
            normalized_value="test",
            source_name="GitHub",
            status="banana",
            confidence=ConfidenceLevel.HIGH,
        )
