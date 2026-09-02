from core.github_mentions import (
    discover_github_mentions,
    extract_github_match_context,
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



def test_extracts_context_around_exact_match():
    text = (
        "Contact information:\n"
        "Phone: TEST_VARIANT\n"
        "Email: test@example.com\n"
    )

    context = extract_github_match_context(
        text,
        "TEST_VARIANT",
    )

    assert context is not None
    assert context["exact_match"] is True
    assert "Phone: TEST_VARIANT" in context["context"]


def test_returns_none_when_exact_match_is_absent():
    context = extract_github_match_context(
        "No relevant value here.",
        "TEST_VARIANT",
    )

    assert context is None


def test_github_mention_preserves_api_url():
    response_data = {
        "items": [
            {
                "path": "README.md",
                "html_url": (
                    "https://github.com/"
                    "example/repo-one/blob/main/README.md"
                ),
                "url": (
                    "https://api.github.com/"
                    "repos/example/repo-one/contents/README.md"
                ),
                "repository": {
                    "full_name": "example/repo-one",
                },
            }
        ]
    }

    mentions = extract_github_mentions(
        response_data,
        matched_variant="TEST_VARIANT",
    )

    assert mentions[0]["api_url"] == (
        "https://api.github.com/"
        "repos/example/repo-one/contents/README.md"
    )


@pytest.mark.asyncio
async def test_fetch_github_file_text_decodes_base64():
    import base64

    from core.github_mentions import fetch_github_file_text

    expected_text = (
        "Contact information:\n"
        "Phone: TEST_VARIANT\n"
    )

    encoded = base64.b64encode(
        expected_text.encode("utf-8")
    ).decode("ascii")

    calls = []

    class FakeResult:
        status_code = 200
        response_data = {
            "encoding": "base64",
            "content": encoded,
        }
        error = None

    class FakeCollector:
        async def request(self, **kwargs):
            calls.append(kwargs)
            return FakeResult()

    result = await fetch_github_file_text(
        FakeCollector(),
        "https://api.github.com/repos/example/repo/contents/file.txt",
    )

    assert result["status"] == "ok"
    assert result["text"] == expected_text
    assert calls[0]["url"] == (
        "https://api.github.com/repos/example/repo/contents/file.txt"
    )


@pytest.mark.asyncio
async def test_verify_github_mention_confirms_exact_match():
    import base64

    from core.github_mentions import verify_github_mention

    text = (
        "Contact information:\n"
        "Phone: TEST_VARIANT\n"
        "Other public information.\n"
    )

    encoded = base64.b64encode(
        text.encode("utf-8")
    ).decode("ascii")

    class FakeResult:
        status_code = 200
        response_data = {
            "encoding": "base64",
            "content": encoded,
        }
        error = None

    class FakeCollector:
        async def request(self, **kwargs):
            return FakeResult()

    mention = {
        "source": "GitHub",
        "repository": "example/repo",
        "path": "contacts.txt",
        "url": (
            "https://github.com/"
            "example/repo/blob/main/contacts.txt"
        ),
        "api_url": (
            "https://api.github.com/"
            "repos/example/repo/contents/contacts.txt"
        ),
        "matched_variant": "TEST_VARIANT",
    }

    verification = await verify_github_mention(
        FakeCollector(),
        mention,
    )

    assert verification["status"] == "verified"
    assert verification["matched_variants"] == [
        "TEST_VARIANT"
    ]
    assert "Phone: TEST_VARIANT" in verification["context"]


@pytest.mark.asyncio
async def test_verify_github_mention_preserves_all_verified_variants():
    import base64

    from core.github_mentions import verify_github_mention

    text = (
        "Primary phone: TEST_VARIANT_A\n"
        "Alternative format: TEST_VARIANT_B\n"
    )

    encoded = base64.b64encode(
        text.encode("utf-8")
    ).decode("ascii")

    class FakeResult:
        status_code = 200
        response_data = {
            "encoding": "base64",
            "content": encoded,
        }
        error = None

    class FakeCollector:
        async def request(self, **kwargs):
            return FakeResult()

    mention = {
        "source": "GitHub",
        "repository": "example/repo",
        "path": "contacts.txt",
        "url": (
            "https://github.com/"
            "example/repo/blob/main/contacts.txt"
        ),
        "api_url": (
            "https://api.github.com/"
            "repos/example/repo/contents/contacts.txt"
        ),
        "matched_variants": [
            "TEST_VARIANT_A",
            "TEST_VARIANT_B",
        ],
    }

    verification = await verify_github_mention(
        FakeCollector(),
        mention,
    )

    assert verification["status"] == "verified"
    assert verification["matched_variants"] == [
        "TEST_VARIANT_A",
        "TEST_VARIANT_B",
    ]
