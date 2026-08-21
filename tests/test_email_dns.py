import dns.resolver

from core.dns_intelligence import (
    extract_email_domain,
    resolve_mx_records,
    resolve_spf_record,
    resolve_dmarc_record,
    collect_email_domain_intelligence,
)


def test_extract_email_domain():
    domain = extract_email_domain(
        "User.Name@Example.COM"
    )

    assert domain == "example.com"



def test_resolve_mx_records(monkeypatch):
    class FakeMX:
        def __init__(self, preference, exchange):
            self.preference = preference
            self.exchange = exchange

    def fake_resolve(domain, record_type):
        assert domain == "example.com"
        assert record_type == "MX"

        return [
            FakeMX(20, "mail2.example.com."),
            FakeMX(10, "mail1.example.com."),
        ]

    monkeypatch.setattr(
        "dns.resolver.resolve",
        fake_resolve,
    )

    records = resolve_mx_records("example.com")

    assert records == [
        {
            "priority": 10,
            "host": "mail1.example.com",
        },
        {
            "priority": 20,
            "host": "mail2.example.com",
        },
    ]



def test_resolve_mx_records_returns_empty_for_nxdomain(monkeypatch):
    def fake_resolve(domain, record_type):
        raise dns.resolver.NXDOMAIN

    monkeypatch.setattr(
        "dns.resolver.resolve",
        fake_resolve,
    )

    records = resolve_mx_records(
        "does-not-exist.example"
    )

    assert records == []



def test_resolve_mx_records_returns_empty_for_no_answer(monkeypatch):
    def fake_resolve(domain, record_type):
        raise dns.resolver.NoAnswer

    monkeypatch.setattr(
        "dns.resolver.resolve",
        fake_resolve,
    )

    records = resolve_mx_records(
        "example.com"
    )

    assert records == []



def test_resolve_spf_record(monkeypatch):
    class FakeTXT:
        strings = (
            b"v=spf1 ",
            b"include:_spf.example.com -all",
        )

    def fake_resolve(domain, record_type):
        assert domain == "example.com"
        assert record_type == "TXT"

        return [FakeTXT()]

    monkeypatch.setattr(
        "dns.resolver.resolve",
        fake_resolve,
    )

    record = resolve_spf_record(
        "example.com"
    )

    assert record == (
        "v=spf1 include:_spf.example.com -all"
    )



def test_resolve_spf_record_returns_none_for_no_answer(monkeypatch):
    def fake_resolve(domain, record_type):
        raise dns.resolver.NoAnswer

    monkeypatch.setattr(
        "dns.resolver.resolve",
        fake_resolve,
    )

    record = resolve_spf_record(
        "example.com"
    )

    assert record is None



def test_resolve_spf_record_returns_none_for_nxdomain(monkeypatch):
    def fake_resolve(domain, record_type):
        raise dns.resolver.NXDOMAIN

    monkeypatch.setattr(
        "dns.resolver.resolve",
        fake_resolve,
    )

    record = resolve_spf_record(
        "does-not-exist.example"
    )

    assert record is None



def test_resolve_dmarc_record(monkeypatch):
    class FakeTXT:
        strings = (
            b"v=DMARC1; ",
            b"p=reject; rua=mailto:dmarc@example.com",
        )

    def fake_resolve(domain, record_type):
        assert domain == "_dmarc.example.com"
        assert record_type == "TXT"

        return [FakeTXT()]

    monkeypatch.setattr(
        "dns.resolver.resolve",
        fake_resolve,
    )

    record = resolve_dmarc_record(
        "example.com"
    )

    assert record == (
        "v=DMARC1; p=reject; "
        "rua=mailto:dmarc@example.com"
    )



def test_resolve_dmarc_record_returns_none_for_no_answer(monkeypatch):
    def fake_resolve(domain, record_type):
        raise dns.resolver.NoAnswer

    monkeypatch.setattr(
        "dns.resolver.resolve",
        fake_resolve,
    )

    record = resolve_dmarc_record(
        "example.com"
    )

    assert record is None



def test_resolve_dmarc_record_returns_none_for_nxdomain(monkeypatch):
    def fake_resolve(domain, record_type):
        raise dns.resolver.NXDOMAIN

    monkeypatch.setattr(
        "dns.resolver.resolve",
        fake_resolve,
    )

    record = resolve_dmarc_record(
        "does-not-exist.example"
    )

    assert record is None



def test_collect_email_domain_intelligence(monkeypatch):
    monkeypatch.setattr(
        "core.dns_intelligence.resolve_mx_records",
        lambda domain: [
            {
                "priority": 10,
                "host": "mail.example.com",
            }
        ],
    )

    monkeypatch.setattr(
        "core.dns_intelligence.resolve_spf_record",
        lambda domain: "v=spf1 -all",
    )

    monkeypatch.setattr(
        "core.dns_intelligence.resolve_dmarc_record",
        lambda domain: "v=DMARC1; p=reject",
    )

    result = collect_email_domain_intelligence(
        "User@Example.COM"
    )

    assert result == {
        "domain": "example.com",
        "mx": [
            {
                "priority": 10,
                "host": "mail.example.com",
            }
        ],
        "spf": "v=spf1 -all",
        "dmarc": "v=DMARC1; p=reject",
    }
