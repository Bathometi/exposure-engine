import hashlib

from core.normalizer import Normalizer
from core.schema import EntityType


class EmailIdentifier:
    """
    Builds deterministic identifiers derived from email addresses.
    """

    @staticmethod
    def gravatar_sha256(email: str) -> str:
        normalized_email = Normalizer.normalize(
            EntityType.EMAIL,
            email,
        )

        return hashlib.sha256(
            normalized_email.encode("utf-8")
        ).hexdigest()


def identity(value: str) -> str:
    """
    Returns the normalized value unchanged.

    This is the default identifier strategy.
    """

    return value


IDENTIFIER_REGISTRY = {
    "identity": identity,
    "gravatar_sha256": EmailIdentifier.gravatar_sha256,
}
