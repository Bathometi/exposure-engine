from types import SimpleNamespace

from core.pivots import collect_next_targets, collect_username_pivots, pivot_to_next_target
from core.schema import StatusEnum


def test_collect_username_pivots_deduplicates_websites():
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

    pivots = collect_username_pivots(
        evidences
    )

    assert pivots == [
        {
            "type": "website",
            "value": "https://example.com",
            "sources": [
                "SourceA",
                "SourceB",
            ],
        }
    ]



def test_pivot_to_next_target_converts_related_username():
    pivot = {
        "type": "related_username",
        "value": "test_variant",
        "sources": [
            "SourceA",
        ],
    }

    target = pivot_to_next_target(
        pivot
    )

    assert target == {
        "target_type": "username",
        "value": "test_variant",
        "sources": [
            "SourceA",
        ],
    }


def test_pivot_to_next_target_converts_website_to_domain():
    pivot = {
        "type": "website",
        "value": "https://example.com/profile",
        "sources": [
            "SourceA",
        ],
    }

    target = pivot_to_next_target(
        pivot
    )

    assert target == {
        "target_type": "domain",
        "value": "example.com",
        "sources": [
            "SourceA",
        ],
    }


def test_pivot_to_next_target_ignores_unknown_type():
    pivot = {
        "type": "unknown",
        "value": "test_value",
        "sources": [
            "SourceA",
        ],
    }

    target = pivot_to_next_target(
        pivot
    )

    assert target is None



def test_collect_next_targets_deduplicates_domains():
    pivots = [
        {
            "type": "website",
            "value": "https://example.com/profile",
            "sources": [
                "SourceA",
            ],
        },
        {
            "type": "website",
            "value": "https://example.com/about",
            "sources": [
                "SourceB",
            ],
        },
    ]

    targets = collect_next_targets(
        pivots
    )

    assert targets == [
        {
            "target_type": "domain",
            "value": "example.com",
            "sources": [
                "SourceA",
                "SourceB",
            ],
        }
    ]
