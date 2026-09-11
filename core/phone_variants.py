import phonenumbers

from core.normalizer import Normalizer


def generate_phone_variants(
    phone: str,
) -> list[str]:
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
    except phonenumbers.NumberParseException:
        return []

    if not phonenumbers.is_possible_number(number):
        return []

    variants = [
        phonenumbers.format_number(
            number,
            phonenumbers.PhoneNumberFormat.E164,
        ),
        phonenumbers.format_number(
            number,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL,
        ),
        phonenumbers.format_number(
            number,
            phonenumbers.PhoneNumberFormat.NATIONAL,
        ),
    ]

    variants.extend(
        variant.replace(" ", "")
        for variant in list(variants)
    )

    e164 = phonenumbers.format_number(
        number,
        phonenumbers.PhoneNumberFormat.E164,
    )

    variants.append(
        e164.lstrip("+")
    )

    return list(
        dict.fromkeys(
            variant
            for variant in variants
            if variant
        )
    )
