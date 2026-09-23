import asyncio
import sys

from check_email import scan_email
from check_ip import scan_ip
from check_phone import scan_phone
from check_username import scan_username
from core.validators import (
    EmailValidator,
    IPValidator,
    PhoneValidator,
    UsernameValidator,
)


def detect_target_type(value: str) -> str | None:
    cleaned = value.strip()

    email_valid, _ = EmailValidator.validate(
        cleaned
    )

    if email_valid:
        return "email"

    phone_valid, _ = PhoneValidator.validate(
        cleaned
    )

    if phone_valid:
        return "phone"

    ip_valid, _ = IPValidator.validate(
        cleaned
    )

    if ip_valid:
        return "ip"

    username_valid, _ = UsernameValidator.validate(
        cleaned
    )

    if username_valid:
        return "username"

    return None


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python exposure.py <target>"
        )
        sys.exit(1)

    target = sys.argv[1]
    verbose = "--verbose" in sys.argv[2:]
    target_type = detect_target_type(target)

    if target_type == "email":
        completed = asyncio.run(
            scan_email(target)
        )
    elif target_type == "username":
        completed = asyncio.run(
            scan_username(
                target,
                verbose=verbose,
            )
        )
    elif target_type == "phone":
        completed = asyncio.run(
            scan_phone(target)
        )
    elif target_type == "ip":
        completed = asyncio.run(
            scan_ip(target)
        )
    else:
        print(
            "Could not determine target type."
        )
        sys.exit(1)

    if not completed:
        sys.exit(1)


if __name__ == "__main__":
    main()
