from core.normalizer import Normalizer
from core.schema import EntityType


def test_email_normalization():
    result = Normalizer.normalize_email(
        "  User.Name@Domain.COM  "
    )

    assert result == "user.name@domain.com"


def test_username_normalization():
    result = Normalizer.normalize_username(
        "  @Somename_123  "
    )

    assert result == "somename_123"


def test_phone_normalization_with_plus():
    result = Normalizer.normalize_phone(
        "+380 (97) 123-45-67"
    )

    assert result == "+380971234567"


def test_phone_normalization_without_plus():
    result = Normalizer.normalize_phone(
        "380 (97) 123-45-67"
    )

    assert result == "380971234567"


def test_generic_normalize_username():
    result = Normalizer.normalize(
        EntityType.USERNAME,
        "  @Test_User  "
    )

    assert result == "test_user"


def test_generic_normalize_email():
    result = Normalizer.normalize(
        EntityType.EMAIL,
        "  TEST@EXAMPLE.COM  "
    )

    assert result == "test@example.com"
