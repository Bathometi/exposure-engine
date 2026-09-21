from core.pivots import collect_username_pivots
from core.schema import StatusEnum


def build_username_summary(
    evidences,
) -> dict:
    found_sources = []
    not_found_sources = []
    attention_sources = []
    identity_signals = []

    for evidence in evidences:
        if evidence.status == StatusEnum.FOUND:
            found_sources.append(
                evidence.source_name
            )

            for field in [
                "name",
                "display_name",
            ]:
                value = evidence.details.get(
                    field
                )

                if value:
                    identity_signals.append(
                        {
                            "source": evidence.source_name,
                            "field": field,
                            "value": value,
                        }
                    )

        elif evidence.status == StatusEnum.NOT_FOUND:
            not_found_sources.append(
                evidence.source_name
            )

        else:
            attention_sources.append(
                {
                    "source": evidence.source_name,
                    "status": evidence.status.value,
                }
            )

    pivots = collect_username_pivots(
        evidences
    )

    return {
        "found_sources": found_sources,
        "not_found_sources": not_found_sources,
        "attention_sources": attention_sources,
        "identity_signals": identity_signals,
        "pivots": pivots,
    }
