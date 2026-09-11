import phonenumbers

from core.phone_variants import (
    generate_phone_variants,
)


def get_example_phone() -> str:
    number = phonenumbers.example_number_for_type(
        "GB",
        phonenumbers.PhoneNumberType.MOBILE,
    )

    assert number is not None

    return phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )


def test_generates_multiple_phone_variants():
    phone = get_example_phone()

    variants = generate_phone_variants(
        phone
    )

    assert len(variants) >= 3
    assert phone in variants


def test_variants_are_unique():
    variants = generate_phone_variants(
        get_example_phone()
    )

    assert len(variants) == len(set(variants))


def test_invalid_phone_returns_no_variants():
    assert generate_phone_variants(
        "not-a-phone"
    ) == []
