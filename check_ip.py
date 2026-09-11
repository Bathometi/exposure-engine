from core.collector import HTTPCollector
from core.internetdb import collect_internetdb_host
from core.normalizer import Normalizer
from core.reporting import save_json_report
from core.schema import EntityType
from core.validators import IPValidator


async def scan_ip(
    raw_ip: str,
) -> bool:
    is_valid, _ = IPValidator.validate(
        raw_ip
    )

    if not is_valid:
        return False

    normalized_ip = Normalizer.normalize_ip(
        raw_ip
    )

    async with HTTPCollector() as collector:
        internetdb = await collect_internetdb_host(
            collector,
            normalized_ip,
        )

    print("\nIP INTELLIGENCE")
    print(
        f"IP: {normalized_ip}"
    )
    print(
        f"InternetDB status: {internetdb['status']}"
    )
    print(
        "Ports: "
        + (
            ", ".join(
                str(port)
                for port in internetdb["ports"]
            )
            or "n/a"
        )
    )
    print(
        "Hostnames: "
        + (
            ", ".join(
                internetdb["hostnames"]
            )
            or "n/a"
        )
    )

    if internetdb["error"]:
        print(
            f"Source error: {internetdb['error']}"
        )

    report_path = save_json_report(
        entity_type=EntityType.IP,
        raw_value=raw_ip,
        normalized_value=normalized_ip,
        evidences=[],
        enrichments={
            "internetdb": internetdb,
        },
    )

    print(
        f"\nReport saved: {report_path}"
    )

    return True
