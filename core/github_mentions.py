import os

def extract_github_mentions(
    response_data: dict,
    matched_variant: str,
) -> list[dict]:
    mentions = []

    if not isinstance(response_data, dict):
        return mentions

    items = response_data.get("items", [])

    if not isinstance(items, list):
        return mentions

    for item in items:
        if not isinstance(item, dict):
            continue

        repository = item.get("repository")

        if not isinstance(repository, dict):
            continue

        full_name = repository.get("full_name")
        path = item.get("path")
        url = item.get("html_url")

        if not full_name or not path or not url:
            continue

        mentions.append(
            {
                "source": "GitHub",
                "repository": full_name,
                "path": path,
                "url": url,
                **({"api_url": item["url"]} if item.get("url") else {}),
                "matched_variant": matched_variant,
            }
        )

    return mentions


GITHUB_CODE_SEARCH_URL = (
    "https://api.github.com/search/code"
)


async def discover_github_mentions(
    collector,
    query: str,
) -> list[dict]:
    headers = {
        "Accept": "application/vnd.github+json",
    }

    github_token = os.getenv(
        "GITHUB_TOKEN"
    )

    if github_token:
        headers["Authorization"] = (
            f"Bearer {github_token}"
        )

    result = await collector.request(
        url=GITHUB_CODE_SEARCH_URL,
        response_type="json",
        headers=headers,
        params={
            "q": f'"{query}"',
            "per_page": "10",
        },
    )

    if result.error is not None:
        return []

    if result.status_code != 200:
        return []

    return extract_github_mentions(
        result.response_data,
        matched_variant=query,
    )


def extract_github_match_context(
    text: str,
    query: str,
    radius: int = 150,
) -> dict | None:
    if not isinstance(text, str):
        return None

    if not isinstance(query, str):
        return None

    if not query:
        return None

    position = text.lower().find(
        query.lower()
    )

    if position == -1:
        return None

    start = max(
        0,
        position - radius,
    )
    end = min(
        len(text),
        position + len(query) + radius,
    )

    return {
        "exact_match": True,
        "context": text[start:end],
    }


async def fetch_github_file_text(
    collector,
    api_url: str,
) -> dict:
    import base64

    headers = {
        "Accept": "application/vnd.github+json",
    }

    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    result = await collector.request(
        url=api_url,
        response_type="json",
        headers=headers,
    )

    if result.error is not None:
        return {
            "status": "error",
            "text": None,
        }

    if result.status_code != 200:
        return {
            "status": "error",
            "text": None,
        }

    data = result.response_data

    if not isinstance(data, dict):
        return {
            "status": "error",
            "text": None,
        }

    if data.get("encoding") != "base64":
        return {
            "status": "error",
            "text": None,
        }

    content = data.get("content")

    if not isinstance(content, str):
        return {
            "status": "error",
            "text": None,
        }

    try:
        text = base64.b64decode(
            content
        ).decode(
            "utf-8",
            errors="replace",
        )
    except Exception:
        return {
            "status": "error",
            "text": None,
        }

    return {
        "status": "ok",
        "text": text,
    }


async def verify_github_mention(
    collector,
    mention: dict,
) -> dict:
    api_url = mention.get("api_url")

    matched_variants = mention.get("matched_variants")

    if not isinstance(matched_variants, list):
        matched_variant = mention.get("matched_variant")
        matched_variants = (
            [matched_variant]
            if isinstance(matched_variant, str)
            else []
        )

    if not api_url:
        return {
            "status": "unavailable",
            "matched_variants": [],
            "context": None,
        }

    fetched = await fetch_github_file_text(
        collector,
        api_url,
    )

    if fetched.get("status") != "ok":
        return {
            "status": "unavailable",
            "matched_variants": [],
            "context": None,
        }

    text = fetched.get("text")

    if not isinstance(text, str):
        return {
            "status": "unavailable",
            "matched_variants": [],
            "context": None,
        }

    verified_variants = []
    verified_context = None

    for variant in matched_variants:
        match = extract_github_match_context(
            text,
            variant,
        )

        if match is not None:
            verified_variants.append(variant)

            if verified_context is None:
                verified_context = match["context"]

    if verified_variants:
        return {
            "status": "verified",
            "matched_variants": verified_variants,
            "context": verified_context,
            "classification": classify_phone_context(
                verified_context
            ),
        }

    return {
        "status": "not_verified",
        "matched_variants": [],
        "context": None,
    }


def classify_phone_context(context: str) -> str:
    import re

    if not isinstance(context, str):
        return "uncertain"

    if re.search(
        r"\b(?:phone|tel|telephone|mobile|whatsapp)\b",
        context,
        re.IGNORECASE,
    ):
        return "phone_context"

    decimal_values = re.findall(
        r"(?<!\w)[+-]?\d+\.\d+(?!\w)",
        context,
    )

    if len(decimal_values) >= 4:
        return "numeric_noise"

    return "uncertain"


async def verify_github_mentions(
    collector,
    mentions: list[dict],
) -> list[dict]:
    results = []

    for mention in mentions:
        verification = await verify_github_mention(
            collector,
            mention,
        )

        verified_mention = {
            **mention,
            "verification": verification,
        }

        results.append(verified_mention)

    return results


def summarize_github_verifications(
    results: list[dict],
) -> dict:
    summary = {
        "candidate_count": len(results),
        "verified_string_occurrences": 0,
        "phone_context": 0,
        "numeric_noise": 0,
        "uncertain": 0,
        "not_verified": 0,
        "unavailable": 0,
    }

    for result in results:
        verification = result.get("verification", {})

        status = verification.get("status")
        classification = verification.get(
            "classification"
        )

        if status == "verified":
            summary["verified_string_occurrences"] += 1

            if classification in {
                "phone_context",
                "numeric_noise",
                "uncertain",
            }:
                summary[classification] += 1

        elif status == "not_verified":
            summary["not_verified"] += 1

        elif status == "unavailable":
            summary["unavailable"] += 1

    return summary
