import asyncio
from core.schema import EntityType
from core.normalizer import Normalizer
from core.collector import HTTPCollector


async def main():
    collector = HTTPCollector(timeout_seconds=5)
    
    # Тестові цілі для перевірки різних HTTP відповідей
    targets = [
        ("GitHub Existing", "https://api.github.com/users/Bathometi"),
        ("GitHub Non-Existing", "https://api.github.com/users/non_existing_user_9999999"),
        ("HTTP 403/Blocked Test", "https://httpbin.org/status/403"),
        ("Timeout Test", "https://httpbin.org/delay/10")  # Таймаут має спрацювати на 5 сек
    ]
    
    tasks = []
    print("\n🚀 Starting Parallel Async HTTP Collection...\n")
    
    for name, url in targets:
        raw_user = name
        norm_user = Normalizer.normalize_username(raw_user)
        
        # Створюємо асинхронні задачі
        task = collector.check_url(
            entity_type=EntityType.USERNAME,
            raw_value=raw_user,
            normalized_value=norm_user,
            url=url,
            source_name="http_collector_test"
        )
        tasks.append(task)
    
    # Запускаємо всі запити одночасно (паралельно)
    results = await asyncio.gather(*tasks)
    
    for evidence in results:
        print(f"[+] Source/Target: {evidence.raw_value}")
        print(f"    Status: {evidence.status.value}")
        print(f"    Confidence: {evidence.confidence.value}")
        print(f"    Details: {evidence.details}\n")


if __name__ == "__main__":
    asyncio.run(main())
