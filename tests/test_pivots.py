from types import SimpleNamespace

from core.pivots import collect_username_pivots
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
