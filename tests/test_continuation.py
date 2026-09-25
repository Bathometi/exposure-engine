import pytest

from core.continuation import (
    build_continuation_action,
    run_continuation_action,
)


def test_username_next_target_is_ready():
    target = {
        "target_type": "username",
        "value": "test_variant",
        "sources": [
            "SourceA",
        ],
    }

    action = build_continuation_action(
        target
    )

    assert action == {
        "status": "ready",
        "scanner": "username",
        "target_type": "username",
        "value": "test_variant",
        "sources": [
            "SourceA",
        ],
    }


def test_domain_next_target_is_unsupported():
    target = {
        "target_type": "domain",
        "value": "example.com",
        "sources": [
            "SourceA",
        ],
    }

    action = build_continuation_action(
        target
    )

    assert action == {
        "status": "unsupported",
        "scanner": None,
        "target_type": "domain",
        "value": "example.com",
        "sources": [
            "SourceA",
        ],
    }


def test_build_continuation_actions_for_next_targets():
    from core.continuation import build_continuation_actions

    targets = [
        {
            "target_type": "username",
            "value": "test_variant",
            "sources": [
                "SourceA",
            ],
        },
        {
            "target_type": "domain",
            "value": "example.com",
            "sources": [
                "SourceB",
            ],
        },
    ]

    actions = build_continuation_actions(
        targets
    )

    assert actions == [
        {
            "status": "ready",
            "scanner": "username",
            "target_type": "username",
            "value": "test_variant",
            "sources": [
                "SourceA",
            ],
        },
        {
            "status": "unsupported",
            "scanner": None,
            "target_type": "domain",
            "value": "example.com",
            "sources": [
                "SourceB",
            ],
        },
    ]



@pytest.mark.asyncio
async def test_run_continuation_action_runs_ready_username():
    received = []

    async def fake_scan_username(value):
        received.append(value)
        return True

    action = {
        "status": "ready",
        "scanner": "username",
        "target_type": "username",
        "value": "test_variant",
        "sources": [
            "SourceA",
        ],
    }

    result = await run_continuation_action(
        action,
        {
            "username": fake_scan_username,
        },
    )

    assert result is True
    assert received == [
        "test_variant",
    ]


@pytest.mark.asyncio
async def test_run_continuation_action_skips_unsupported_target():
    called = []

    async def fake_scanner(value):
        called.append(value)
        return True

    action = {
        "status": "unsupported",
        "scanner": None,
        "target_type": "domain",
        "value": "example.com",
        "sources": [
            "SourceA",
        ],
    }

    result = await run_continuation_action(
        action,
        {
            "username": fake_scanner,
        },
    )

    assert result is False
    assert called == []
