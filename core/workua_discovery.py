import re
import xml.etree.ElementTree as ET
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



def extract_workua_sitemap_entries(xml_text: str) -> list[dict]:
    if not isinstance(xml_text, str):
        return []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    namespace = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    }

    entries = []

    for url_element in root.findall("sm:url", namespace):
        loc_element = url_element.find("sm:loc", namespace)

        if loc_element is None or not loc_element.text:
            continue

        parsed_url = parse_workua_url(
            loc_element.text.strip()
        )

        if parsed_url is None:
            continue

        lastmod_element = url_element.find(
            "sm:lastmod",
            namespace,
        )

        entry = dict(parsed_url)
        entry["lastmod"] = (
            lastmod_element.text.strip()
            if lastmod_element is not None
            and lastmod_element.text
            else None
        )

        entries.append(entry)

    return entries
