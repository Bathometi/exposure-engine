from core.collector import HTTPCollector
from core.github_mentions import (
    summarize_github_verifications,
    verify_github_mentions,
)
from core.normalizer import Normalizer
from core.phone_intelligence import collect_phone_intelligence
from core.phone_mentions import discover_phone_github_mentions
from core.reporting import save_json_report
from core.schema import EntityType
from core.validators import PhoneValidator


async def scan_phone(
    raw_phone: str,
) -> bool:
    is_valid, _ = PhoneValidator.validate(
        raw_phone
    )

    if not is_valid:
        return False

    intelligence = collect_phone_intelligence(
        raw_phone
    )

    print("\nPHONE INTELLIGENCE")
    print(
        f"Possible: {intelligence['possible']}"
    )
    print(
        f"Valid: {intelligence['valid']}"
    )
    print(
        f"Region: {intelligence['region'] or 'n/a'}"
    )
    print(
        f"Location: {intelligence['location'] or 'n/a'}"
    )
    print(
        f"Carrier: {intelligence['carrier'] or 'n/a'}"
    )
    print(
        f"Type: {intelligence['type']}"
    )
    print(
        "Timezone: "
        + (
            ", ".join(
                intelligence["timezones"]
            )
            or "n/a"
        )
    )

    async with HTTPCollector() as collector:
        mentions = await discover_phone_github_mentions(
            collector,
            raw_phone,
        )

        verified = await verify_github_mentions(
            collector,
            mentions,
        )

    summary = summarize_github_verifications(
        verified
    )

    print("\nGITHUB PHONE MENTIONS")
    print(
        f"Candidates: "
        f"{summary['candidate_count']}"
    )
    print(
        "Verified string occurrences: "
        f"{summary['verified_string_occurrences']}"
    )
    print(
        f"Phone context: "
        f"{summary['phone_context']}"
    )
    print(
        "Example/test data: "
        f"{summary['example_or_test_data']}"
    )
    print(
        f"Numeric noise: "
        f"{summary['numeric_noise']}"
    )
    print(
        f"Uncertain: "
        f"{summary['uncertain']}"
    )
    print(
        f"Not verified: "
        f"{summary['not_verified']}"
    )
    print(
        f"Unavailable: "
        f"{summary['unavailable']}"
    )

    normalized_phone = Normalizer.normalize_phone(
        raw_phone
    )

    report_path = save_json_report(
        entity_type=EntityType.PHONE,
        raw_value=raw_phone,
        normalized_value=normalized_phone,
        evidences=[],
        enrichments={
            "phone_intelligence": intelligence,
        },
        analysis={
            "github_phone_mentions": {
                "summary": summary,
                "results": verified,
            }
        },
    )

    print(
        f"\nReport saved: {report_path}"
    )

    return True
