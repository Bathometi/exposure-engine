import hashlib

from core.identifiers import EmailIdentifier


def test_gravatar_identifier_uses_normalized_email():
    email = "user@example.com"

    expected = hashlib.sha256(
        email.encode("utf-8")
    ).hexdigest()

    result = EmailIdentifier.gravatar_sha256(
        email
    )

    assert result == expected


def test_gravatar_identifier_normalizes_before_hashing():
    raw_email = "  User@Example.COM  "

    expected = hashlib.sha256(
        b"user@example.com"
    ).hexdigest()

    result = EmailIdentifier.gravatar_sha256(
        raw_email
    )

    assert result == expected


def test_gravatar_identifier_is_deterministic():
    first = EmailIdentifier.gravatar_sha256(
        "test@example.com"
    )

    second = EmailIdentifier.gravatar_sha256(
        "test@example.com"
    )

    assert first == second


def test_gravatar_identifier_matches_official_example():
    result = EmailIdentifier.gravatar_sha256(
        "MyEmailAddress@example.com "
    )

    assert result == (
        "84059b07d4be67b806386c0aad8070a23"
        "f18836bbaae342275dc0a83414c32ee"
    )
