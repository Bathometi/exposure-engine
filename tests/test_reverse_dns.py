from unittest.mock import patch

from core.reverse_dns import collect_reverse_dns


def test_reverse_dns_success_returns_structured_result():
    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.return_value = [
            "dns.example.test."
        ]

        result = collect_reverse_dns(
            "192.0.2.1"
        )

    assert result == {
        "status": "ok",
        "source": "Reverse DNS",
        "ip": "192.0.2.1",
        "hostnames": [
            "dns.example.test",
        ],
        "error": None,
    }


def test_reverse_dns_no_answer_means_not_found():
    import dns.resolver

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.side_effect = (
            dns.resolver.NoAnswer
        )

        result = collect_reverse_dns(
            "192.0.2.1"
        )

    assert result == {
        "status": "not_found",
        "source": "Reverse DNS",
        "ip": "192.0.2.1",
        "hostnames": [],
        "error": None,
    }


def test_reverse_dns_timeout_means_unavailable():
    import dns.exception

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.side_effect = (
            dns.exception.Timeout
        )

        result = collect_reverse_dns(
            "192.0.2.1"
        )

    assert result == {
        "status": "unavailable",
        "source": "Reverse DNS",
        "ip": "192.0.2.1",
        "hostnames": [],
        "error": "DNS timeout",
    }


def test_reverse_dns_no_nameservers_means_unavailable():
    import dns.resolver

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.side_effect = (
            dns.resolver.NoNameservers
        )

        result = collect_reverse_dns(
            "192.0.2.1"
        )

    assert result == {
        "status": "unavailable",
        "source": "Reverse DNS",
        "ip": "192.0.2.1",
        "hostnames": [],
        "error": "DNS nameservers unavailable",
    }
