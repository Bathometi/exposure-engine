from core.workua_discovery import (
    extract_workua_sitemap_entries,
)


def test_extracts_workua_resume_sitemap_entries():
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.work.ua/resumes/11582424/</loc>
        <lastmod>2026-08-29</lastmod>
    </url>
    <url>
        <loc>https://www.work.ua/resumes/11107897/</loc>
        <lastmod>2026-08-29</lastmod>
    </url>
</urlset>
"""

    entries = extract_workua_sitemap_entries(
        xml_text
    )

    assert entries == [
        {
            "resource_type": "resume",
            "resource_id": "11582424",
            "canonical_url": (
                "https://www.work.ua/resumes/11582424/"
            ),
            "lastmod": "2026-08-29",
        },
        {
            "resource_type": "resume",
            "resource_id": "11107897",
            "canonical_url": (
                "https://www.work.ua/resumes/11107897/"
            ),
            "lastmod": "2026-08-29",
        },
    ]


def test_sitemap_skips_unrecognized_workua_urls():
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.work.ua/resumes-python/</loc>
    </url>
</urlset>
"""

    entries = extract_workua_sitemap_entries(
        xml_text
    )

    assert entries == []


def test_sitemap_handles_missing_lastmod():
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.work.ua/jobs/8365632/</loc>
    </url>
</urlset>
"""

    entries = extract_workua_sitemap_entries(
        xml_text
    )

    assert entries == [
        {
            "resource_type": "job",
            "resource_id": "8365632",
            "canonical_url": (
                "https://www.work.ua/jobs/8365632/"
            ),
            "lastmod": None,
        }
    ]


def test_sitemap_handles_invalid_xml():
    entries = extract_workua_sitemap_entries(
        "<urlset>"
    )

    assert entries == []


def test_sitemap_handles_non_string():
    entries = extract_workua_sitemap_entries(None)

    assert entries == []
