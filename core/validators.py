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

        if any(char.isspace() for char in cleaned):
            return False, "Username cannot contain whitespace."

        if len(cleaned) > cls.MAX_LENGTH:
            return False, "Username is too long."

        return True, None
