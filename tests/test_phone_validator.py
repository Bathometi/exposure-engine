import pytest

from core.validators import PhoneValidator


@pytest.mark.parametrize(
    "phone",
    [
        "+380501234567",
        "380501234567",
        "+380 50 123 45 67",
        "+380 (50) 123-45-67",
        "1234567",
    ],
)
def test_valid_phone_numbers_are_accepted(phone):
    is_valid, reason = PhoneValidator.validate(phone)

    assert is_valid is True
    assert reason is None


@pytest.mark.parametrize(
    ("phone", "expected_reason"),
    [
        (
            "",
            "Phone number cannot be empty.",
        ),
        (
            "   ",
            "Phone number cannot be empty.",
        ),
        (
            "12345",
            "Phone number is too short.",
        ),
        (
            "1234567890123456",
            "Phone number is too long.",
        ),
        (
            "test1234567",
            "Phone number contains invalid characters.",
        ),
        (
            "test@example.com",
            "Phone number contains invalid characters.",
        ),
        (
            "380+501234567",
            "Phone number contains invalid characters.",
        ),
    ],
)
def test_invalid_phone_numbers_are_rejected(
    phone,
    expected_reason,
):
    is_valid, reason = PhoneValidator.validate(phone)

    assert is_valid is False
    assert reason == expected_reason


def test_phone_rejects_invalid_utf8_surrogate():
    invalid_phone = "\udcd1+380501234567"

    is_valid, reason = PhoneValidator.validate(invalid_phone)

    assert is_valid is False
    assert reason == "Phone number contains invalid Unicode characters."
