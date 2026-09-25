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
        "pivots": [],
        "next_targets": [],
        "continuation_actions": [],
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


def test_build_username_summary_collects_website_pivots():
    evidences = [
        SimpleNamespace(
            source_name="SourceA",
            status=StatusEnum.FOUND,
            details={
                "website_url": "https://example.com",
            },
        ),
        SimpleNamespace(
            source_name="SourceB",
            status=StatusEnum.FOUND,
            details={
                "website_url": "https://example.com",
            },
        ),
    ]

    summary = build_username_summary(
        evidences
    )

    assert summary["pivots"] == [
        {
            "type": "website",
            "value": "https://example.com",
            "sources": [
                "SourceA",
                "SourceB",
            ],
        }
    ]


def test_build_username_summary_collects_related_username_pivots():
    evidences = [
        SimpleNamespace(
            source_name="SourceA",
            status=StatusEnum.FOUND,
            details={
                "github_username": "TEST_VARIANT",
            },
        ),
        SimpleNamespace(
            source_name="SourceB",
            status=StatusEnum.FOUND,
            details={
                "github_username": "TEST_VARIANT",
            },
        ),
    ]

    summary = build_username_summary(
        evidences
    )

    assert {
        "type": "related_username",
        "value": "test_variant",
        "sources": [
            "SourceA",
            "SourceB",
        ],
    } in summary["pivots"]


def test_build_username_summary_normalizes_website_pivots():
    evidences = [
        SimpleNamespace(
            source_name="SourceA",
            status=StatusEnum.FOUND,
            details={
                "website_url": "https://EXAMPLE.com/",
            },
        ),
        SimpleNamespace(
            source_name="SourceB",
            status=StatusEnum.FOUND,
            details={
                "website_url": "https://example.com",
            },
        ),
    ]

    summary = build_username_summary(
        evidences
    )

    assert summary["pivots"] == [
        {
            "type": "website",
            "value": "https://example.com",
            "sources": [
                "SourceA",
                "SourceB",
            ],
        }
    ]


def test_build_username_summary_normalizes_related_username_pivots():
    evidences = [
        SimpleNamespace(
            source_name="SourceA",
            status=StatusEnum.FOUND,
            details={
                "github_username": "@TEST_VARIANT",
            },
        ),
        SimpleNamespace(
            source_name="SourceB",
            status=StatusEnum.FOUND,
            details={
                "twitter_username": "test_variant",
            },
        ),
    ]

    summary = build_username_summary(
        evidences
    )

    assert {
        "type": "related_username",
        "value": "test_variant",
        "sources": [
            "SourceA",
            "SourceB",
        ],
    } in summary["pivots"]


def test_build_username_summary_collects_next_targets():
    evidences = [
        SimpleNamespace(
            source_name="SourceA",
            status=StatusEnum.FOUND,
            details={
                "website_url": "https://example.com/profile",
            },
        ),
    ]

    summary = build_username_summary(
        evidences
    )

    assert summary["next_targets"] == [
        {
            "target_type": "domain",
            "value": "example.com",
            "sources": [
                "SourceA",
            ],
        }
    ]


def test_build_username_summary_adds_continuation_actions():
    evidences = [
        SimpleNamespace(
            source_name="SourceA",
            status=StatusEnum.FOUND,
            details={
                "github_username": "TEST_VARIANT",
            },
        ),
    ]

    summary = build_username_summary(
        evidences
    )

    assert summary["continuation_actions"] == [
        {
            "status": "ready",
            "scanner": "username",
            "target_type": "username",
            "value": "test_variant",
            "sources": [
                "SourceA",
            ],
        }
    ]
