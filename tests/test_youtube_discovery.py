import pytest

from core.youtube_discovery import (
    discover_youtube_channels,
    extract_search_candidates,
)


def test_extracts_youtube_search_candidates():
    response_data = {
        "items": [
            {
                "id": {
                    "channelId": "UC111",
                },
                "snippet": {
                    "title": "Candidate One",
                    "description": "",
                },
            },
            {
                "id": {
                    "channelId": "UC222",
                },
                "snippet": {
                    "title": "Candidate Two",
                    "description": "making nonsense",
                },
            },
        ]
    }

    candidates = extract_search_candidates(
        response_data
    )

    assert candidates == [
        {
            "channel_id": "UC111",
            "title": "Candidate One",
            "description": "",
        },
        {
            "channel_id": "UC222",
            "title": "Candidate Two",
            "description": "making nonsense",
        },
    ]
def test_extract_search_candidates_skips_invalid_items():
    response_data = {
        "items": [
            None,
            {},
            {
                "id": {},
                "snippet": {
                    "title": "No channel id",
                },
            },
            {
                "id": {
                    "channelId": "UC111",
                },
                "snippet": {
                    "title": "Valid Channel",
                    "description": "",
                },
            },
        ]
    }

    candidates = extract_search_candidates(
        response_data
    )

    assert candidates == [
        {
            "channel_id": "UC111",
            "title": "Valid Channel",
            "description": "",
        }
    ]
def test_extract_search_candidates_handles_non_dict_response():
    candidates = extract_search_candidates(None)

    assert candidates == []
@pytest.mark.asyncio
async def test_discover_youtube_channels_uses_search_api(monkeypatch):
    calls = []

    class FakeResult:
        status_code = 200
        response_data = {
            "items": [
                {
                    "id": {
                        "channelId": "UC111",
                    },
                    "snippet": {
                        "title": "Candidate One",
                        "description": "",
                    },
                }
            ]
        }
        error = None

    class FakeCollector:
        def _resolve_query_params(
            self,
            platform_config,
            request_value,
        ):
            assert request_value == "test_username"
            return {
                "part": "snippet",
                "q": "test_username",
                "type": "channel",
                "maxResults": "5",
                "key": "test-key",
            }

        async def request(self, **kwargs):
            calls.append(kwargs)
            return FakeResult()

    candidates = await discover_youtube_channels(
        FakeCollector(),
        "test_username",
    )

    assert candidates == [
        {
            "channel_id": "UC111",
            "title": "Candidate One",
            "description": "",
        }
    ]

    assert calls == [
        {
            "url": (
                "https://www.googleapis.com/"
                "youtube/v3/search"
            ),
            "response_type": "json",
            "params": {
                "part": "snippet",
                "q": "test_username",
                "type": "channel",
                "maxResults": "5",
                "key": "test-key",
            },
        }
    ]
