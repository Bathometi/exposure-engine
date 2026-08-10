import asyncio
import sys
from core.schema import EntityType
from core.normalizer import Normalizer
from core.collector import HTTPCollector
from config.platforms import PLATFORMS


async def scan_target(target_username: str):
    norm_user = Normalizer.normalize_username(target_username)
    
    print(f"\n🔍 [Target]: '{target_username}' -> Normalized: '{norm_user}'")
    print("⚡ Scanning platforms using Platform-Specific Detectors...\n" + "="*60)

    collector = HTTPCollector(timeout_seconds=5)
    tasks = []

    # Формуємо асинхронні задачі з опиранням на PLATFORMS config
    for platform_name, config in PLATFORMS.items():
        task = collector.check_platform(
            entity_type=EntityType.USERNAME,
            raw_value=target_username,
            normalized_value=norm_user,
            source_name=platform_name,
            platform_config=config
        )
        tasks.append(task)

    # Безпечний gather з return_exceptions=True за порадою ментора
    results = await asyncio.gather(*tasks, return_exceptions=True)

    found_count = 0
    for result in results:
        # Перевірка на неперехоплені exceptions
        if isinstance(result, Exception):
            print(f"⚠️ [Collector Error]: {result}")
            continue

        evidence = result
        is_found = evidence.status == evidence.status.FOUND
        is_not_found = evidence.status == evidence.status.NOT_FOUND
        
        status_symbol = "🟢" if is_found else "🔴" if is_not_found else "⚠️"
        
        print(f"{status_symbol} [{evidence.source_name}] Status: {evidence.status.value.upper()}")
        print(f"   URL: {evidence.details.get('target_url')}")
        
        if is_found:
            found_count += 1
            # Виводимо точкові чисті деталі замість звалища raw_json
            for key in ("name", "created_at", "public_repos"):
                if evidence.details.get(key):
                    print(f"   {key.capitalize()}: {evidence.details[key]}")
        print("-" * 60)

    print(f"\n🎯 Done! Found active target on {found_count}/{len(PLATFORMS)} platforms.\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        username_to_check = sys.argv[1]
    else:
        username_to_check = input("Введи юзернейм для пошуку: ")

    asyncio.run(scan_target(username_to_check))
