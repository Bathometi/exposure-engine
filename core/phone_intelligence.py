import phonenumbers
from phonenumbers import (
    carrier,
    geocoder,
    timezone,
)

from core.normalizer import Normalizer


def collect_phone_intelligence(
    phone: str,
) -> dict[str, object]:
    normalized = Normalizer.normalize_phone(
        phone
    )

    parse_value = (
        normalized
        if normalized.startswith("+")
        else f"+{normalized}"
    )

    try:
        number = phonenumbers.parse(
            parse_value,
            None,
        )
    except phonenumbers.NumberParseException as exc:
        return {
            "possible": False,
            "valid": False,
            "region": None,
            "location": None,
            "carrier": None,
            "type": "UNKNOWN",
            "timezones": [],
            "parse_error": str(exc),
        }

    return {
        "possible": phonenumbers.is_possible_number(
            number
        ),
        "valid": phonenumbers.is_valid_number(
            number
        ),
        "region": phonenumbers.region_code_for_number(
            number
        ),
        "location": (
            geocoder.description_for_number(
                number,
                "en",
            )
            or None
        ),
        "carrier": (
            carrier.name_for_number(
                number,
                "en",
            )
            or None
        ),
        "type": phonenumbers.PhoneNumberType.to_string(
            phonenumbers.number_type(
                number
            )
        ),
        "timezones": list(
            timezone.time_zones_for_number(
                number
            )
        ),
    }
