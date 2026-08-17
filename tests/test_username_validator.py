import pytest

from core.validators import UsernameValidator


@pytest.mark.parametrize(
    "username",
    [
        "alice",
        "some_name",
        "some-name",
        "user.name",
        "12345",
    ],
)
def test_valid_usernames_are_accepted(username):
    is_valid, reason = UsernameValidator.validate(username)

    assert is_valid is True
    assert reason is None


@pytest.mark.parametrize(
    ("username", "expected_reason"),
    [
        (
            "",
            "Username cannot be empty.",
        ),
        (
            "   ",
            "Username cannot be empty.",
        ),
        (
            "john doe",
            "Username cannot contain whitespace.",
        ),
        (
            "a" * 129,
            "Username is too long.",
        ),
    ],
)
def test_invalid_usernames_are_rejected(
    username,
    expected_reason,
):
    is_valid, reason = UsernameValidator.validate(username)

    assert is_valid is False
    assert reason == expected_reason
