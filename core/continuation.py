def build_continuation_action(
    target,
) -> dict:
    target_type = target.get(
        "target_type"
    )

    if target_type == "username":
        return {
            "status": "ready",
            "scanner": "username",
            "target_type": target_type,
            "value": target.get(
                "value"
            ),
            "sources": target.get(
                "sources",
                [],
            ),
        }

    return {
        "status": "unsupported",
        "scanner": None,
        "target_type": target_type,
        "value": target.get(
            "value"
        ),
        "sources": target.get(
            "sources",
            [],
        ),
    }


def build_continuation_actions(
    targets,
) -> list[dict]:
    return [
        build_continuation_action(
            target
        )
        for target in targets
    ]


async def run_continuation_action(
    action,
    scanners,
):
    if action.get("status") != "ready":
        return False

    scanner_name = action.get(
        "scanner"
    )

    scanner = scanners.get(
        scanner_name
    )

    if scanner is None:
        return False

    return await scanner(
        action.get("value")
    )
