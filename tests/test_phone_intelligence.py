import phonenumbers

from core.phone_intelligence import (
    collect_phone_intelligence,
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


def test_collects_phone_intelligence():
    result = collect_phone_intelligence(
        get_example_phone()
    )

    assert result["possible"] is True
    assert result["valid"] is True
    assert result["region"] == "GB"
    assert result["type"] == "MOBILE"
    assert isinstance(
        result["timezones"],
        list,
    )


def test_accepts_international_digits_without_plus():
    phone = get_example_phone().lstrip("+")

    result = collect_phone_intelligence(
        phone
    )

    assert result["possible"] is True
    assert result["valid"] is True
    assert result["region"] == "GB"


def test_invalid_phone_returns_parse_error():
    result = collect_phone_intelligence(
        "not-a-phone"
    )

    assert result["possible"] is False
    assert result["valid"] is False
    assert result["parse_error"]
