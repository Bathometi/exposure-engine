from core.github_mentions import (
    discover_github_mentions,
    extract_github_mentions,
)


def test_extracts_github_code_mentions():
    response_data = {
        "total_count": 2,
        "incomplete_results": False,
        "items": [
            {
                "name": "README.md",
                "path": "README.md",
                "html_url": (
                    "https://github.com/"
                    "example/repo-one/blob/main/README.md"
                ),
                "repository": {
                    "full_name": "example/repo-one",
                },
            },
            {
                "name": "contacts.txt",
                "path": "data/contacts.txt",
                "html_url": (
                    "https://github.com/"
                    "example/repo-two/blob/main/data/contacts.txt"
                ),
                "repository": {
                    "full_name": "example/repo-two",
                },
            },
        ],
    }

    mentions = extract_github_mentions(
        response_data,
        matched_variant="TEST_VARIANT",
    )

    assert mentions == [
        {
            "source": "GitHub",
            "repository": "example/repo-one",
            "path": "README.md",
            "url": (
                "https://github.com/"
                "example/repo-one/blob/main/README.md"
            ),
            "matched_variant": "TEST_VARIANT",
        },
        {
            "source": "GitHub",
            "repository": "example/repo-two",
            "path": "data/contacts.txt",
            "url": (
                "https://github.com/"
                "example/repo-two/blob/main/data/contacts.txt"
            ),
            "matched_variant": "TEST_VARIANT",
        },
    ]


def test_ignores_malformed_github_items():
    response_data = {
        "items": [
            None,
            {},
            {
                "path": "README.md",
            },
        ],
    }

    mentions = extract_github_mentions(
        response_data,
        matched_variant="TEST_VARIANT",
    )

    assert mentions == []



import pytest


@pytest.mark.asyncio
async def test_discover_github_mentions_uses_code_search(
    monkeypatch,
):
    calls = []

    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "test-github-token",
    )

    class FakeResult:
        status_code = 200
        response_data = {
            "items": [
                {
                    "path": "README.md",
                    "html_url": (
                        "https://github.com/"
                        "example/repo-one/blob/main/README.md"
                    ),
                    "repository": {
                        "full_name": "example/repo-one",
                    },
                }
            ]
        }
        error = None

    class FakeCollector:
        async def request(self, **kwargs):
            calls.append(kwargs)
            return FakeResult()

    mentions = await discover_github_mentions(
        FakeCollector(),
        "TEST_VARIANT",
    )

    assert mentions == [
        {
            "source": "GitHub",
            "repository": "example/repo-one",
            "path": "README.md",
            "url": (
                "https://github.com/"
                "example/repo-one/blob/main/README.md"
            ),
            "matched_variant": "TEST_VARIANT",
        }
    ]

    assert calls == [
        {
            "url": "https://api.github.com/search/code",
            "response_type": "json",
            "headers": {
                "Accept": "application/vnd.github+json",
                "Authorization": "Bearer test-github-token",
            },
            "params": {
                "q": '"TEST_VARIANT"',
                "per_page": "10",
            },
        }
    ]


import pytest


@pytest.mark.asyncio
async def test_discover_github_mentions_handles_http_error():
    class FakeResult:
        status_code = 403
        response_data = {
            "message": "Forbidden",
        }
        error = None

    class FakeCollector:
        async def request(self, **kwargs):
            return FakeResult()

    mentions = await discover_github_mentions(
        FakeCollector(),
        "TEST_VARIANT",
    )

    assert mentions == []


@pytest.mark.asyncio
async def test_discover_github_mentions_handles_request_error():
    class FakeResult:
        status_code = 0
        response_data = None
        error = "network error"

    class FakeCollector:
        async def request(self, **kwargs):
            return FakeResult()

    mentions = await discover_github_mentions(
        FakeCollector(),
        "TEST_VARIANT",
    )

    assert mentions == []
