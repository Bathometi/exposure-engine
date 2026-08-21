import dns.resolver

def extract_email_domain(email: str) -> str:
    return email.rsplit("@", 1)[-1].lower()


def resolve_mx_records(domain: str) -> list[dict[str, object]]:
    try:
        answers = dns.resolver.resolve(domain, "MX")
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
    ):
        return []

    records = [
        {
            "priority": int(answer.preference),
            "host": str(answer.exchange).rstrip("."),
        }
        for answer in answers
    ]

    return sorted(
        records,
        key=lambda record: record["priority"],
    )


def resolve_spf_record(domain: str) -> str | None:
    try:
        answers = dns.resolver.resolve(domain, "TXT")
    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
    ):
        return None

    for answer in answers:
        value = b"".join(
            answer.strings
        ).decode("utf-8")

        if value.lower().startswith("v=spf1"):
            return value

    return None


def resolve_dmarc_record(domain: str) -> str | None:
    try:
        answers = dns.resolver.resolve(
            f"_dmarc.{domain}",
            "TXT",
        )
    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
    ):
        return None

    for answer in answers:
        value = b"".join(
            answer.strings
        ).decode("utf-8")

        if value.lower().startswith("v=dmarc1"):
            return value

    return None


def collect_email_domain_intelligence(email: str) -> dict[str, object]:
    domain = extract_email_domain(email)

    return {
        "domain": domain,
        "mx": resolve_mx_records(domain),
        "spf": resolve_spf_record(domain),
        "dmarc": resolve_dmarc_record(domain),
    }

