from types import SimpleNamespace

from core.schema import StatusEnum
from core.username_summary import build_username_summary


def test_build_username_summary_groups_sources():
    evidences = [
        SimpleNamespace(
            source_name="GitLab",
            status=StatusEnum.FOUND,
            details={},
        ),
        SimpleNamespace(
            source_name="Telegram",
            status=StatusEnum.FOUND,
            details={},
        ),
        SimpleNamespace(
            source_name="GitHub",
            status=StatusEnum.NOT_FOUND,
            details={},
        ),
        SimpleNamespace(
            source_name="Reddit",
            status=StatusEnum.BLOCKED,
            details={},
        ),
        SimpleNamespace(
            source_name="Keybase",
            status=StatusEnum.UNKNOWN,
            details={},
        ),
    ]

    summary = build_username_summary(
        evidences
    )

    assert summary == {
        "found_sources": [
            "GitLab",
            "Telegram",
        ],
        "not_found_sources": [
            "GitHub",
        ],
        "attention_sources": [
            {
                "source": "Reddit",
                "status": "blocked",
            },
            {
                "source": "Keybase",
                "status": "unknown",
            },
        ],
        "identity_signals": [],
    }


def test_build_username_summary_extracts_identity_signals():
    evidences = [
        SimpleNamespace(
            source_name="GitLab",
            status=StatusEnum.FOUND,
            details={
                "name": "Test User",
            },
        ),
        SimpleNamespace(
            source_name="Telegram",
            status=StatusEnum.FOUND,
            details={
                "display_name": "Test Display",
            },
        ),
    ]

    summary = build_username_summary(
        evidences
    )

    assert summary["identity_signals"] == [
        {
            "source": "GitLab",
            "field": "name",
            "value": "Test User",
        },
        {
            "source": "Telegram",
            "field": "display_name",
            "value": "Test Display",
        },
    ]
