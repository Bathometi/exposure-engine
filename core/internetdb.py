async def collect_internetdb_host(
    collector,
    ip: str,
) -> dict:
    result = await collector.request(
        url=f"https://internetdb.shodan.io/{ip}",
        response_type="json",
    )

    if result.error is not None:
        return {
            "status": "unavailable",
            "source": "Shodan InternetDB",
            "ip": ip,
            "ports": [],
            "hostnames": [],
            "cpes": [],
            "tags": [],
            "vulns": [],
            "error": str(result.error),
        }

    if result.status_code == 404:
        return {
            "status": "not_indexed",
            "source": "Shodan InternetDB",
            "ip": ip,
            "ports": [],
            "hostnames": [],
            "cpes": [],
            "tags": [],
            "vulns": [],
            "error": None,
        }

    if result.status_code != 200:
        return {
            "status": "unavailable",
            "source": "Shodan InternetDB",
            "ip": ip,
            "ports": [],
            "hostnames": [],
            "cpes": [],
            "tags": [],
            "vulns": [],
            "error": f"HTTP {result.status_code}",
        }

    data = result.response_data or {}

    return {
        "status": "ok",
        "source": "Shodan InternetDB",
        "ip": data.get("ip"),
        "ports": data.get("ports", []),
        "hostnames": data.get("hostnames", []),
        "cpes": data.get("cpes", []),
        "tags": data.get("tags", []),
        "vulns": data.get("vulns", []),
        "error": None,
    }
