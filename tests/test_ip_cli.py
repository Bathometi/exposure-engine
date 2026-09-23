import pytest

import check_ip
from core.schema import EntityType


@pytest.mark.asyncio
async def test_scan_ip_saves_internetdb_rdap_and_reverse_dns(monkeypatch):
    target = "192.0.2.1"
    saved = {}

    internetdb = {
        "status": "ok",
        "source": "Shodan InternetDB",
        "ip": target,
        "ports": [443],
        "hostnames": ["example.test"],
        "cpes": [],
        "tags": [],
        "vulns": [],
        "error": None,
    }

    rdap = {
        "status": "ok",
        "source": "RDAP",
        "ip": target,
        "handle": "TEST-NET",
        "name": "TEST-NETWORK",
        "start_address": "192.0.2.0",
        "end_address": "192.0.2.255",
        "country": "ZZ",
        "type": "DIRECT ALLOCATION",
        "error": None,
    }

    reverse_dns = {
        "status": "ok",
        "source": "Reverse DNS",
        "ip": target,
        "hostnames": ["dns.example.test"],
        "error": None,
    }

    forward_dns = {
        "status": "ok",
        "source": "Forward DNS Verification",
        "ip": target,
        "confirmed_hostnames": ["dns.example.test"],
        "results": [
            {
                "hostname": "dns.example.test",
                "addresses": [target],
                "matches_ip": True,
            }
        ],
        "error": None,
    }

    collector_instance = object()

    class FakeHTTPCollector:
        def __init__(
            self,
            max_retries=3,
        ):
            assert max_retries == 1

        async def __aenter__(self):
            return collector_instance

        async def __aexit__(
            self,
            exc_type,
            exc,
            traceback,
        ):
            return False

    async def fake_internetdb(collector, ip):
        assert collector is collector_instance
        assert ip == target
        return internetdb

    async def fake_rdap(collector, ip):
        assert collector is collector_instance
        assert ip == target
        return rdap

    def fake_reverse_dns(ip):
        assert ip == target
        return reverse_dns

    def fake_forward_dns(ip, hostnames):
        assert ip == target
        assert hostnames == ["dns.example.test"]
        return forward_dns

    def fake_save_json_report(**kwargs):
        saved.update(kwargs)
        return "report.json"

    monkeypatch.setattr(
        check_ip,
        "HTTPCollector",
        FakeHTTPCollector,
    )
    monkeypatch.setattr(
        check_ip,
        "collect_internetdb_host",
        fake_internetdb,
    )
    monkeypatch.setattr(
        check_ip,
        "collect_rdap_ip",
        fake_rdap,
    )
    monkeypatch.setattr(
        check_ip,
        "collect_reverse_dns",
        fake_reverse_dns,
        raising=False,
    )
    monkeypatch.setattr(
        check_ip,
        "verify_forward_dns",
        fake_forward_dns,
        raising=False,
    )
    monkeypatch.setattr(
        check_ip,
        "save_json_report",
        fake_save_json_report,
    )

    result = await check_ip.scan_ip(target)

    assert result is True
    assert saved["entity_type"] == EntityType.IP
    assert saved["raw_value"] == target
    assert saved["normalized_value"] == target
    assert saved["evidences"] == []

    assert saved["enrichments"] == {
        "internetdb": internetdb,
        "rdap": rdap,
        "reverse_dns": reverse_dns,
        "forward_dns": forward_dns,
    }
