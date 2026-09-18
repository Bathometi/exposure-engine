from urllib.parse import urlsplit, urlunsplit

from core.normalizer import Normalizer
from core.schema import StatusEnum


def normalize_website_url(value: str) -> str:
    cleaned = value.strip()
    parsed = urlsplit(cleaned)

    if not parsed.scheme or not parsed.netloc:
        return cleaned.rstrip("/")

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    path = (
        ""
        if parsed.path == "/"
        else parsed.path
    )

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            parsed.query,
            parsed.fragment,
        )
    )


def collect_username_pivots(
    evidences,
) -> list[dict]:
    pivot_index = {}

    pivot_fields = [
        (
            "website",
            "website_url",
        ),
        (
            "related_username",
            "github_username",
        ),
        (
            "related_username",
            "twitter_username",
        ),
    ]

    for evidence in evidences:
        if evidence.status != StatusEnum.FOUND:
            continue

        for pivot_type, field in pivot_fields:
            value = evidence.details.get(
                field
            )

            if not value:
                continue

            if pivot_type == "website":
                value = normalize_website_url(
                    value
                )

            elif pivot_type == "related_username":
                value = Normalizer.normalize_username(
                    value
                )

            key = (
                pivot_type,
                value,
            )

            if key not in pivot_index:
                pivot_index[key] = []

            if (
                evidence.source_name
                not in pivot_index[key]
            ):
                pivot_index[key].append(
                    evidence.source_name
                )

    pivots = []

    for (
        pivot_type,
        value,
    ), sources in pivot_index.items():
        pivots.append(
            {
                "type": pivot_type,
                "value": value,
                "sources": sources,
            }
        )

    return pivots
