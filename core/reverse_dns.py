import dns.exception
import dns.resolver
import dns.reversename


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
