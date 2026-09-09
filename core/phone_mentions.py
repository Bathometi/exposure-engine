from core.github_mentions import (
    discover_github_mentions,
)
from core.phone_variants import (
    generate_phone_variants,
)


async def discover_phone_github_mentions(
    collector,
    phone: str,
) -> dict:
    variants = generate_phone_variants(
        phone
    )

    mentions = []
    mentions_by_key = {}
    searches = []

    for variant in variants:
        result = await discover_github_mentions(
            collector,
            variant,
        )

        searches.append({
            "variant": variant,
            "status": result["status"],
            "error": result["error"],
        })

        for mention in result["mentions"]:
            key = (
                mention.get("source"),
                mention.get("repository"),
                mention.get("path"),
                mention.get("url"),
            )

            matched_variant = mention.get(
                "matched_variant"
            )

            existing = mentions_by_key.get(
                key
            )

            if existing is not None:
                if (
                    matched_variant
                    and matched_variant
                    not in existing["matched_variants"]
                ):
                    existing[
                        "matched_variants"
                    ].append(
                        matched_variant
                    )

                continue

            stored_mention = dict(
                mention
            )

            stored_mention[
                "matched_variants"
            ] = (
                [matched_variant]
                if matched_variant
                else []
            )

            mentions_by_key[key] = (
                stored_mention
            )
            mentions.append(
                stored_mention
            )

    statuses = [
        search["status"]
        for search in searches
    ]

    if statuses and all(
        status == "unavailable"
        for status in statuses
    ):
        status = "unavailable"
    elif "unavailable" in statuses:
        status = "partial"
    else:
        status = "ok"

    return {
        "status": status,
        "mentions": mentions,
        "searches": searches,
    }
