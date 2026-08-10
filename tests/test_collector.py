import pytest
from core.schema import EntityType, StatusEnum
from core.collector import HTTPCollector
from config.platforms import PLATFORMS


@pytest.mark.asyncio
async def test_check_platform_github():
    collector = HTTPCollector(timeout_seconds=5)
    
    # Перевірка валідного акаунта GitHub
    evidence = await collector.check_platform(
        entity_type=EntityType.USERNAME,
        raw_value="octocat",
        normalized_value="octocat",
        source_name="GitHub",
        platform_config=PLATFORMS["GitHub"]
    )
    
    assert evidence.status == StatusEnum.FOUND
    assert evidence.source_name == "GitHub"
    assert "target_url" in evidence.details
