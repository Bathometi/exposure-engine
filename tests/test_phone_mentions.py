import pytest

from core.phone_mentions import (
    discover_phone_github_mentions,
)


@pytest.mark.asyncio
async def test_phone_mentions_merge_and_deduplicate(
    monkeypatch,
):
    monkeypatch.setattr(
        "core.phone_mentions.generate_phone_variants",
        lambda value: [
            "TEST_VARIANT_A",
            "TEST_VARIANT_B",
        ],
    )

    async def fake_discover(
        collector,
        query,
    ):
        common = {
            "source": "GitHub",
            "repository": "example/repo-one",
            "path": "README.md",
            "url": (
                "https://github.com/"
                "example/repo-one/blob/main/README.md"
            ),
            "matched_variant": query,
        }

        if query == "TEST_VARIANT_A":
            return [common]

        return [
            common,
            {
                "source": "GitHub",
                "repository": "example/repo-two",
                "path": "contacts.txt",
                "url": (
                    "https://github.com/"
                    "example/repo-two/blob/main/contacts.txt"
                ),
                "matched_variant": query,
            },
        ]

    monkeypatch.setattr(
        "core.phone_mentions.discover_github_mentions",
        fake_discover,
    )

    mentions = await discover_phone_github_mentions(
        object(),
        "TEST_PHONE",
    )

    assert len(mentions) == 2

    assert mentions[0]["repository"] == "example/repo-one"
    assert mentions[1]["repository"] == "example/repo-two"


@pytest.mark.asyncio
async def test_phone_mentions_preserve_all_matching_variants(
    monkeypatch,
):
    monkeypatch.setattr(
        "core.phone_mentions.generate_phone_variants",
        lambda value: [
            "TEST_VARIANT_A",
            "TEST_VARIANT_B",
        ],
    )

    async def fake_discover(
        collector,
        query,
    ):
        return [
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
        ]

    monkeypatch.setattr(
        "core.phone_mentions.discover_github_mentions",
        fake_discover,
    )

    mentions = await discover_phone_github_mentions(
        object(),
        "TEST_PHONE",
    )

    assert len(mentions) == 1
    assert mentions[0]["matched_variants"] == [
        "TEST_VARIANT_A",
        "TEST_VARIANT_B",
    ]
