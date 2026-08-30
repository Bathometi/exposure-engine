import re
from urllib.parse import urlparse


WORKUA_HOSTS = {
    "work.ua",
    "www.work.ua",
}

WORKUA_URL_PATTERNS = (
    (
        "company",
        re.compile(r"^/jobs/by-company/(\d+)/?$"),
    ),
    (
        "resume",
        re.compile(r"^/resumes/(\d+)/?$"),
    ),
    (
        "job",
        re.compile(r"^/jobs/(\d+)/?$"),
    ),
)


def parse_workua_url(url: str) -> dict | None:
    if not isinstance(url, str):
        return None

    parsed = urlparse(url.strip())

    if parsed.scheme not in {"http", "https"}:
        return None

    if parsed.netloc.lower() not in WORKUA_HOSTS:
        return None

    for resource_type, pattern in WORKUA_URL_PATTERNS:
        match = pattern.fullmatch(parsed.path)

        if match is None:
            continue

        resource_id = match.group(1)

        return {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "canonical_url": (
                "https://www.work.ua"
                f"{parsed.path.rstrip('/')}/"
            ),
        }

    return None
