import ipaddress
import dns.exception
import dns.resolver
import dns.reversename


DNS_LIFETIME = 3.0


def collect_reverse_dns(
    ip: str,
) -> dict:
    reverse_name = dns.reversename.from_address(
        ip
    )

    try:
        answers = dns.resolver.resolve(
            reverse_name,
            "PTR",
            lifetime=DNS_LIFETIME,
        )
    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
    ):
        return {
            "status": "not_found",
            "source": "Reverse DNS",
            "ip": ip,
            "hostnames": [],
            "error": None,
        }
    except dns.exception.Timeout:
        return {
            "status": "unavailable",
            "source": "Reverse DNS",
            "ip": ip,
            "hostnames": [],
            "error": "DNS timeout",
        }
    except dns.resolver.NoNameservers:
        return {
            "status": "unavailable",
            "source": "Reverse DNS",
            "ip": ip,
            "hostnames": [],
            "error": "DNS nameservers unavailable",
        }

    hostnames = [
        str(answer).rstrip(".")
        for answer in answers
    ]

    return {
        "status": "ok",
        "source": "Reverse DNS",
        "ip": ip,
        "hostnames": hostnames,
        "error": None,
    }


def verify_forward_dns(
    ip: str,
    hostnames: list[str],
) -> dict:
    if not hostnames:
        return {
            "status": "not_applicable",
            "source": "Forward DNS Verification",
            "ip": ip,
            "confirmed_hostnames": [],
            "results": [],
            "error": None,
        }

    results = []
    confirmed_hostnames = []
    unavailable_error = None
    completed_lookups = 0

    ip_version = ipaddress.ip_address(ip).version
    record_type = (
        "AAAA"
        if ip_version == 6
        else "A"
    )

    for hostname in hostnames:
        try:
            answers = dns.resolver.resolve(
                hostname,
                record_type,
                lifetime=DNS_LIFETIME,
            )
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
        ):
            completed_lookups += 1
            results.append(
                {
                    "hostname": hostname,
                    "addresses": [],
                    "matches_ip": False,
                }
            )
            continue
        except dns.exception.Timeout:
            unavailable_error = "DNS timeout"
            results.append(
                {
                    "hostname": hostname,
                    "addresses": [],
                    "matches_ip": False,
                    "error": unavailable_error,
                }
            )
            continue

        except dns.resolver.NoNameservers:
            unavailable_error = "DNS nameservers unavailable"
            results.append(
                {
                    "hostname": hostname,
                    "addresses": [],
                    "matches_ip": False,
                    "error": unavailable_error,
                }
            )
            continue

        completed_lookups += 1

        addresses = [
            str(answer)
            for answer in answers
        ]

        matches_ip = ip in addresses

        if matches_ip:
            confirmed_hostnames.append(
                hostname
            )

        results.append(
            {
                "hostname": hostname,
                "addresses": addresses,
                "matches_ip": matches_ip,
            }
        )

    return {
        "status": (
            "partial"
            if unavailable_error and completed_lookups
            else (
                "unavailable"
                if unavailable_error
                else "ok"
            )
        ),
        "source": "Forward DNS Verification",
        "ip": ip,
        "confirmed_hostnames": confirmed_hostnames,
        "results": results,
        "error": unavailable_error,
    }
