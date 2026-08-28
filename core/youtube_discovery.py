def extract_search_candidates(response_data: dict) -> list[dict]:
    candidates = []

    if not isinstance(response_data, dict):
        return candidates

    items = response_data.get("items", [])

    if not isinstance(items, list):
        return candidates

    for item in items:
        if not isinstance(item, dict):
            continue

        item_id = item.get("id", {})
        snippet = item.get("snippet", {})

        if not isinstance(item_id, dict):
            continue

        if not isinstance(snippet, dict):
            snippet = {}

        channel_id = item_id.get("channelId")

        if not channel_id:
            continue

        candidates.append(
            {
                "channel_id": channel_id,
                "title": snippet.get("title"),
                "description": snippet.get("description"),
            }
        )

    return candidates
YOUTUBE_SEARCH_URL = (
    "https://www.googleapis.com/"
    "youtube/v3/search"
)

YOUTUBE_SEARCH_CONFIG = {
    "query_params": {
        "part": "snippet",
        "q": "{value}",
        "type": "channel",
        "maxResults": "5",
    },
    "query_params_from_env": {
        "key": "YOUTUBE_API_KEY",
    },
}


async def discover_youtube_channels(
    collector,
    query: str,
) -> list[dict]:
    params = collector._resolve_query_params(
        YOUTUBE_SEARCH_CONFIG,
        query,
    )

    result = await collector.request(
        url=YOUTUBE_SEARCH_URL,
        response_type="json",
        params=params,
    )

    if result.error is not None:
        return []

    if result.status_code != 200:
        return []

    return extract_search_candidates(
        result.response_data
    )
