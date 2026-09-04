import phonenumbers
import pytest

from core.validators import PhoneValidator


_example_number = phonenumbers.example_number_for_type(
    "GB",
    phonenumbers.PhoneNumberType.MOBILE,
)

_example_e164 = phonenumbers.format_number(
    _example_number,
    phonenumbers.PhoneNumberFormat.E164,
)

_example_digits = _example_e164.lstrip("+")

_example_international = phonenumbers.format_number(
    _example_number,
    phonenumbers.PhoneNumberFormat.INTERNATIONAL,
)

_example_formatted = (
    f"+{_example_digits[:2]} "
    f"({_example_digits[2:6]}) "
    f"{_example_digits[6:9]}-"
    f"{_example_digits[9:]}"
)


@pytest.mark.parametrize(
    "phone",
    [
        _example_e164,
        _example_digits,
        _example_international,
        _example_formatted,
        "1" * 7,
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
            "1" * 5,
            "Phone number is too short.",
        ),
        (
            "1" * 16,
            "Phone number is too long.",
        ),
        (
            f"test{_example_digits}",
            "Phone number contains invalid characters.",
        ),
        (
            "test@example.com",
            "Phone number contains invalid characters.",
        ),
        (
            (
                f"{_example_digits[:3]}"
                f"+{_example_digits[3:]}"
            ),
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
    invalid_phone = f"\udcd1{_example_e164}"

    is_valid, reason = PhoneValidator.validate(
        invalid_phone
    )

    assert is_valid is False
    assert reason == (
        "Phone number contains invalid Unicode characters."
    )
