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
    assert verification["classification"] == "phone_context"


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


def test_classifies_clear_phone_context():
    from core.github_mentions import classify_phone_context

    result = classify_phone_context(
        "Contact details:\nPhone: TEST_VARIANT\nEmail: test@example.com"
    )

    assert result == "phone_context"


@pytest.mark.parametrize(
    "context",
    [
        "Tel: TEST_VARIANT",
        "Telephone: TEST_VARIANT",
        "Mobile: TEST_VARIANT",
        "WhatsApp: TEST_VARIANT",
    ],
)
def test_classifies_common_phone_context_markers(context):
    from core.github_mentions import classify_phone_context

    assert classify_phone_context(context) == "phone_context"


def test_classifies_dense_decimal_data_as_numeric_noise():
    from core.github_mentions import classify_phone_context

    context = (
        "0.123456, 0.654321, 0.111111, "
        "0.222222, 0.333333, 0.444444"
    )

    assert classify_phone_context(context) == "numeric_noise"


@pytest.mark.asyncio
async def test_verify_github_mention_classifies_numeric_noise():
    import base64

    from core.github_mentions import verify_github_mention

    text = (
        "0.123456, 0.654321, TEST_VARIANT, "
        "0.111111, 0.222222, 0.333333"
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
        "path": "data.txt",
        "url": (
            "https://github.com/"
            "example/repo/blob/main/data.txt"
        ),
        "api_url": (
            "https://api.github.com/"
            "repos/example/repo/contents/data.txt"
        ),
        "matched_variant": "TEST_VARIANT",
    }

    verification = await verify_github_mention(
        FakeCollector(),
        mention,
    )

    assert verification["status"] == "verified"
    assert verification["classification"] == "numeric_noise"


@pytest.mark.asyncio
async def test_verify_github_mentions_verifies_all_candidates():
    import base64

    from core.github_mentions import verify_github_mentions

    contents = {
        "https://api.github.com/repos/example/repo/contents/contact.txt": (
            "Phone: TEST_VARIANT"
        ),
        "https://api.github.com/repos/example/repo/contents/data.txt": (
            "0.111111, 0.222222, TEST_VARIANT, "
            "0.333333, 0.444444"
        ),
    }

    class FakeCollector:
        async def request(self, **kwargs):
            text = contents[kwargs["url"]]

            class FakeResult:
                status_code = 200
                response_data = {
                    "encoding": "base64",
                    "content": base64.b64encode(
                        text.encode("utf-8")
                    ).decode("ascii"),
                }
                error = None

            return FakeResult()

    mentions = [
        {
            "source": "GitHub",
            "repository": "example/repo",
            "path": "contact.txt",
            "url": "https://github.com/example/repo/contact.txt",
            "api_url": (
                "https://api.github.com/"
                "repos/example/repo/contents/contact.txt"
            ),
            "matched_variant": "TEST_VARIANT",
        },
        {
            "source": "GitHub",
            "repository": "example/repo",
            "path": "data.txt",
            "url": "https://github.com/example/repo/data.txt",
            "api_url": (
                "https://api.github.com/"
                "repos/example/repo/contents/data.txt"
            ),
            "matched_variant": "TEST_VARIANT",
        },
    ]

    results = await verify_github_mentions(
        FakeCollector(),
        mentions,
    )

    assert len(results) == 2
    assert results[0]["verification"]["classification"] == (
        "phone_context"
    )
    assert results[1]["verification"]["classification"] == (
        "numeric_noise"
    )


def test_summarizes_github_verifications():
    from core.github_mentions import summarize_github_verifications

    results = [
        {
            "verification": {
                "status": "verified",
                "classification": "phone_context",
            }
        },
        {
            "verification": {
                "status": "verified",
                "classification": "numeric_noise",
            }
        },
        {
            "verification": {
                "status": "verified",
                "classification": "uncertain",
            }
        },
        {
            "verification": {
                "status": "not_verified",
                "classification": None,
            }
        },
        {
            "verification": {
                "status": "unavailable",
                "classification": None,
            }
        },
    ]

    summary = summarize_github_verifications(results)

    assert summary == {
        "candidate_count": 5,
        "verified_string_occurrences": 3,
        "phone_context": 1,
        "example_or_test_data": 0,
        "numeric_noise": 1,
        "uncertain": 1,
        "not_verified": 1,
        "unavailable": 1,
    }


def test_classifies_explicit_example_phone_data():
    from core.github_mentions import classify_phone_context

    context = (
        'country: "United Kingdom", '
        'example: "TEST_VARIANT"'
    )

    assert classify_phone_context(context) == (
        "example_or_test_data"
    )


def test_classifies_phone_in_spec_file_as_test_data():
    from core.github_mentions import classify_phone_context

    context = (
        'otp = service.verify_create('
        '"TEST_VARIANT", "template")'
    )

    result = classify_phone_context(
        context,
        path="spec/services/message_service_spec.rb",
    )

    assert result == "example_or_test_data"


@pytest.mark.asyncio
async def test_verify_github_mention_uses_file_path_for_classification():
    import base64

    from core.github_mentions import verify_github_mention

    text = 'service.verify_create("TEST_VARIANT", "template")'

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
        "path": "spec/services/message_service_spec.rb",
        "url": (
            "https://github.com/"
            "example/repo/blob/main/spec/services/message_service_spec.rb"
        ),
        "api_url": (
            "https://api.github.com/"
            "repos/example/repo/contents/"
            "spec/services/message_service_spec.rb"
        ),
        "matched_variant": "TEST_VARIANT",
    }

    verification = await verify_github_mention(
        FakeCollector(),
        mention,
    )

    assert verification["status"] == "verified"
    assert verification["classification"] == (
        "example_or_test_data"
    )


@pytest.mark.parametrize(
    "path",
    [
        "e2e/app.spec.js",
        "tests/phone_test.py",
        "src/components/phone.spec.js",
    ],
)
def test_classifies_common_test_file_paths(path):
    from core.github_mentions import classify_phone_context

    result = classify_phone_context(
        'register_number("TEST_VARIANT")',
        path=path,
    )

    assert result == "example_or_test_data"


def test_summary_counts_example_or_test_data():
    from core.github_mentions import summarize_github_verifications

    results = [
        {
            "verification": {
                "status": "verified",
                "classification": "example_or_test_data",
            }
        }
    ]

    summary = summarize_github_verifications(results)

    assert summary["example_or_test_data"] == 1


def test_rejects_phone_digits_embedded_inside_larger_number():
    import phonenumbers

    from core.github_mentions import extract_github_match_context

    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )

    variant = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    ).lstrip("+")

    text = f"999{variant}888,53"

    context = extract_github_match_context(
        text,
        variant,
    )

    assert context is None
