import exposure


def test_detects_username_target():
    assert (
        exposure.detect_target_type(
            "test_username"
        )
        == "username"
    )


def test_detects_username_with_at_prefix():
    assert (
        exposure.detect_target_type(
            "@test_username"
        )
        == "username"
    )


def test_detects_email_target():
    assert (
        exposure.detect_target_type(
            "test@example.com"
        )
        == "email"
    )


def test_rejects_empty_target():
    assert exposure.detect_target_type("   ") is None


def test_launcher_dispatches_username(monkeypatch):
    received = []

    async def fake_scan_username(value):
        received.append(value)
        return True

    async def fake_scan_email(value):
        raise AssertionError(
            "email scan should not run"
        )

    monkeypatch.setattr(
        exposure,
        "scan_username",
        fake_scan_username,
    )
    monkeypatch.setattr(
        exposure,
        "scan_email",
        fake_scan_email,
    )
    monkeypatch.setattr(
        exposure.sys,
        "argv",
        [
            "exposure.py",
            "test_username",
        ],
    )

    exposure.main()

    assert received == ["test_username"]


def test_launcher_dispatches_email(monkeypatch):
    received = []

    async def fake_scan_email(value):
        received.append(value)
        return True

    async def fake_scan_username(value):
        raise AssertionError(
            "username scan should not run"
        )

    monkeypatch.setattr(
        exposure,
        "scan_email",
        fake_scan_email,
    )
    monkeypatch.setattr(
        exposure,
        "scan_username",
        fake_scan_username,
    )
    monkeypatch.setattr(
        exposure.sys,
        "argv",
        [
            "exposure.py",
            "test@example.com",
        ],
    )

    exposure.main()

    assert received == ["test@example.com"]
