import pytest

import core.phone_mentions as phone_mentions


@pytest.mark.asyncio
async def test_phone_discovery_preserves_partial_failure(
    monkeypatch,
):
    monkeypatch.setattr(
        phone_mentions,
        "generate_phone_variants",
        lambda phone: [
            "TEST_VARIANT_A",
            "TEST_VARIANT_B",
        ],
    )

    async def fake_discover(collector, query):
        if query == "TEST_VARIANT_A":
            return {
                "status": "ok",
                "mentions": [
                    {
                        "source": "GitHub",
                        "repository": "example/repo-one",
                        "path": "README.md",
                        "url": (
                            "https://github.com/"
                            "example/repo-one/blob/main/README.md"
                        ),
                        "matched_variant": query,
                    }
                ],
                "error": None,
            }

        return {
            "status": "unavailable",
            "mentions": [],
            "error": "HTTP 503",
        }

    monkeypatch.setattr(
        phone_mentions,
        "discover_github_mentions",
        fake_discover,
    )

    result = await (
        phone_mentions.discover_phone_github_mentions(
            object(),
            "TEST_PHONE",
        )
    )

    assert result["status"] == "partial"
    assert len(result["mentions"]) == 1

    assert result["mentions"][0]["matched_variants"] == [
        "TEST_VARIANT_A",
    ]

    assert result["searches"] == [
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
    ]
