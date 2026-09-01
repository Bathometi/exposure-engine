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
