from core.collector import HTTPCollector
from core.internetdb import collect_internetdb_host
from core.normalizer import Normalizer
from core.rdap import collect_rdap_ip
from core.reverse_dns import (
    collect_reverse_dns,
    verify_forward_dns,
)
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

        rdap = await collect_rdap_ip(
            collector,
            normalized_ip,
        )

    reverse_dns = collect_reverse_dns(
        normalized_ip
    )

    forward_dns = verify_forward_dns(
        normalized_ip,
        reverse_dns["hostnames"],
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
            f"InternetDB error: {internetdb['error']}"
        )

    print(
        f"RDAP status: {rdap['status']}"
    )
    print(
        f"Network: {rdap['name'] or 'n/a'}"
    )
    print(
        "Range: "
        f"{rdap['start_address'] or 'n/a'}"
        " - "
        f"{rdap['end_address'] or 'n/a'}"
    )
    print(
        f"Allocation type: {rdap['type'] or 'n/a'}"
    )

    if rdap["error"]:
        print(
            f"RDAP error: {rdap['error']}"
        )

    print(
        f"Reverse DNS status: {reverse_dns['status']}"
    )
    print(
        "PTR hostnames: "
        + (
            ", ".join(
                reverse_dns["hostnames"]
            )
            or "n/a"
        )
    )

    if reverse_dns["error"]:
        print(
            f"Reverse DNS error: {reverse_dns['error']}"
        )

    print(
        f"Forward DNS status: {forward_dns['status']}"
    )
    print(
        "Confirmed PTR hostnames: "
        + (
            ", ".join(
                forward_dns["confirmed_hostnames"]
            )
            or "n/a"
        )
    )

    if forward_dns["error"]:
        print(
            f"Forward DNS error: {forward_dns['error']}"
        )

    report_path = save_json_report(
        entity_type=EntityType.IP,
        raw_value=raw_ip,
        normalized_value=normalized_ip,
        evidences=[],
        enrichments={
            "internetdb": internetdb,
            "rdap": rdap,
            "reverse_dns": reverse_dns,
            "forward_dns": forward_dns,
        },
    )

    print(
        f"\nReport saved: {report_path}"
    )

    return True
