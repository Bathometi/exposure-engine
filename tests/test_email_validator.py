import pytest

from core.validators import EmailValidator


@pytest.mark.parametrize(
    "email",
    [
        "user@example.com",
        "user.name@example.com",
        "user+tag@example.com",
        "test123@sub.example.org",
        "x@y.io",
    ],
)
def test_valid_emails_are_accepted(email):
    is_valid, reason = EmailValidator.validate(email)

    assert is_valid is True
    assert reason is None


@pytest.mark.parametrize(
    ("email", "expected_reason"),
    [
        (
            "",
            "Email cannot be empty.",
        ),
        (
            "   ",
            "Email cannot be empty.",
        ),
        (
            "user example@example.com",
            "Email cannot contain whitespace.",
        ),
        (
            "userexample.com",
            "Email must contain exactly one @ symbol.",
        ),
        (
            "user@@example.com",
            "Email must contain exactly one @ symbol.",
        ),
        (
            "@example.com",
            "Email local part cannot be empty.",
        ),
        (
            "user@",
            "Email domain cannot be empty.",
        ),
    ],
)
def test_invalid_emails_are_rejected(
    email,
    expected_reason,
):
    is_valid, reason = EmailValidator.validate(email)

    assert is_valid is False
    assert reason == expected_reason
