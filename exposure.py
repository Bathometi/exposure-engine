import asyncio
import sys

from check_email import scan_email
from check_phone import scan_phone
from check_username import scan_username
from core.validators import (
    EmailValidator,
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
    target_type = detect_target_type(target)

    if target_type == "email":
        completed = asyncio.run(
            scan_email(target)
        )
    elif target_type == "username":
        completed = asyncio.run(
            scan_username(target)
        )
    elif target_type == "phone":
        completed = asyncio.run(
            scan_phone(target)
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
