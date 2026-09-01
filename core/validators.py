from typing import Optional, Tuple


class UsernameValidator:
    """
    Performs basic sanity validation for usernames.

    Platform-specific username rules belong to individual
    platform logic, not to this global validator.
    """

    MAX_LENGTH = 128

    @classmethod
    def validate(
        cls,
        username: str,
    ) -> Tuple[bool, Optional[str]]:
        cleaned = username.strip()

        if not cleaned:
            return False, "Username cannot be empty."

        try:
            cleaned.encode("utf-8")
        except UnicodeEncodeError:
            return False, "Username contains invalid Unicode characters."

        if any(char.isspace() for char in cleaned):
            return False, "Username cannot contain whitespace."

        if len(cleaned) > cls.MAX_LENGTH:
            return False, "Username is too long."

        return True, None


class PhoneValidator:
    """
    Performs basic sanity validation for phone numbers.

    This validator accepts common separators but does not
    attempt country-specific number validation.
    """

    MIN_DIGITS = 7
    MAX_DIGITS = 15
    ALLOWED_SEPARATORS = {" ", "-", "(", ")"}

    @classmethod
    def validate(
        cls,
        phone: str,
    ) -> Tuple[bool, Optional[str]]:
        cleaned = phone.strip()

        if not cleaned:
            return False, "Phone number cannot be empty."

        try:
            cleaned.encode("utf-8")
        except UnicodeEncodeError:
            return False, "Phone number contains invalid Unicode characters."

        for index, char in enumerate(cleaned):
            if char.isdigit():
                continue

            if char == "+" and index == 0:
                continue

            if char in cls.ALLOWED_SEPARATORS:
                continue

            return False, "Phone number contains invalid characters."

        digits = "".join(
            char
            for char in cleaned
            if char.isdigit()
        )

        if len(digits) < cls.MIN_DIGITS:
            return False, "Phone number is too short."

        if len(digits) > cls.MAX_DIGITS:
            return False, "Phone number is too long."

        return True, None


class EmailValidator:
    """
    Performs basic sanity validation for email addresses.

    This validator intentionally checks only obvious structural
    problems. It does not attempt to implement the full email RFC.
    """

    @classmethod
    def validate(
        cls,
        email: str,
    ) -> Tuple[bool, Optional[str]]:
        cleaned = email.strip()

        if not cleaned:
            return False, "Email cannot be empty."

        try:
            cleaned.encode("utf-8")
        except UnicodeEncodeError:
            return False, "Email contains invalid Unicode characters."

        if any(char.isspace() for char in cleaned):
            return False, "Email cannot contain whitespace."

        if cleaned.count("@") != 1:
            return False, "Email must contain exactly one @ symbol."

        local_part, domain = cleaned.split("@", 1)

        if not local_part:
            return False, "Email local part cannot be empty."

        if not domain:
            return False, "Email domain cannot be empty."

        return True, None
