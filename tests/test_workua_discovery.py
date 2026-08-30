from core.workua_discovery import parse_workua_url


def test_parse_workua_resume_url():
    result = parse_workua_url(
        "https://www.work.ua/resumes/19738936/"
    )

    assert result == {
        "resource_type": "resume",
        "resource_id": "19738936",
        "canonical_url": (
            "https://www.work.ua/resumes/19738936/"
        ),
    }


def test_parse_workua_job_url():
    result = parse_workua_url(
        "https://www.work.ua/jobs/8365632/"
    )

    assert result == {
        "resource_type": "job",
        "resource_id": "8365632",
        "canonical_url": (
            "https://www.work.ua/jobs/8365632/"
        ),
    }


def test_parse_workua_company_url():
    result = parse_workua_url(
        "https://www.work.ua/jobs/by-company/717168/"
    )

    assert result == {
        "resource_type": "company",
        "resource_id": "717168",
        "canonical_url": (
            "https://www.work.ua/jobs/by-company/717168/"
        ),
    }


def test_parse_workua_url_normalizes_host_and_trailing_slash():
    result = parse_workua_url(
        "http://work.ua/resumes/19738936"
    )

    assert result == {
        "resource_type": "resume",
        "resource_id": "19738936",
        "canonical_url": (
            "https://www.work.ua/resumes/19738936/"
        ),
    }


def test_parse_workua_url_rejects_other_domains():
    result = parse_workua_url(
        "https://example.com/resumes/19738936/"
    )

    assert result is None


def test_parse_workua_url_rejects_search_pages():
    result = parse_workua_url(
        "https://www.work.ua/resumes-python+developer/"
    )

    assert result is None


def test_parse_workua_url_rejects_non_string():
    result = parse_workua_url(None)

    assert result is None
