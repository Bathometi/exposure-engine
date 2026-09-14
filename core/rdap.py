async def collect_rdap_ip(
    collector,
    ip: str,
) -> dict:
    result = await collector.request(
        url=f"https://rdap.org/ip/{ip}",
        response_type="json",
    )

    if result.error is not None:
        return {
            "status": "unavailable",
            "source": "RDAP",
            "ip": ip,
            "handle": None,
            "name": None,
            "start_address": None,
            "end_address": None,
            "country": None,
            "type": None,
            "error": str(result.error),
        }

    if result.status_code == 404:
        return {
            "status": "not_found",
            "source": "RDAP",
            "ip": ip,
            "handle": None,
            "name": None,
            "start_address": None,
            "end_address": None,
            "country": None,
            "type": None,
            "error": None,
        }

    if result.status_code != 200:
        return {
            "status": "unavailable",
            "source": "RDAP",
            "ip": ip,
            "handle": None,
            "name": None,
            "start_address": None,
            "end_address": None,
            "country": None,
            "type": None,
            "error": f"HTTP {result.status_code}",
        }

    data = result.response_data or {}

    return {
        "status": "ok",
        "source": "RDAP",
        "ip": ip,
        "handle": data.get("handle"),
        "name": data.get("name"),
        "start_address": data.get("startAddress"),
        "end_address": data.get("endAddress"),
        "country": data.get("country"),
        "type": data.get("type"),
        "error": None,
    }
