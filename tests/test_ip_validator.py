from core.validators import IPValidator


def test_accepts_valid_ipv4():
    valid, error = IPValidator.validate(
        "192.0.2.1"
    )

    assert valid is True
    assert error is None
