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


def test_forward_dns_confirms_matching_ipv4():
    from core.reverse_dns import verify_forward_dns

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.return_value = [
            "192.0.2.1"
        ]

        result = verify_forward_dns(
            "192.0.2.1",
            ["dns.example.test"],
        )

    assert result == {
        "status": "ok",
        "source": "Forward DNS Verification",
        "ip": "192.0.2.1",
        "confirmed_hostnames": [
            "dns.example.test",
        ],
        "results": [
            {
                "hostname": "dns.example.test",
                "addresses": [
                    "192.0.2.1",
                ],
                "matches_ip": True,
            }
        ],
        "error": None,
    }

    mock_resolve.assert_called_once_with(
        "dns.example.test",
        "A",
        lifetime=3.0,
    )


def test_forward_dns_rejects_nonmatching_ipv4():
    from core.reverse_dns import verify_forward_dns

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.return_value = [
            "198.51.100.10"
        ]

        result = verify_forward_dns(
            "192.0.2.1",
            ["dns.example.test"],
        )

    assert result == {
        "status": "ok",
        "source": "Forward DNS Verification",
        "ip": "192.0.2.1",
        "confirmed_hostnames": [],
        "results": [
            {
                "hostname": "dns.example.test",
                "addresses": [
                    "198.51.100.10",
                ],
                "matches_ip": False,
            }
        ],
        "error": None,
    }


def test_forward_dns_uses_aaaa_for_ipv6():
    from core.reverse_dns import verify_forward_dns

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.return_value = [
            "2001:db8::1"
        ]

        result = verify_forward_dns(
            "2001:db8::1",
            ["dns.example.test"],
        )

    assert result["confirmed_hostnames"] == [
        "dns.example.test",
    ]

    assert result["results"] == [
        {
            "hostname": "dns.example.test",
            "addresses": [
                "2001:db8::1",
            ],
            "matches_ip": True,
        }
    ]

    mock_resolve.assert_called_once_with(
        "dns.example.test",
        "AAAA",
        lifetime=3.0,
    )


def test_forward_dns_no_answer_means_not_confirmed():
    import dns.resolver

    from core.reverse_dns import verify_forward_dns

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.side_effect = (
            dns.resolver.NoAnswer
        )

        result = verify_forward_dns(
            "192.0.2.1",
            ["dns.example.test"],
        )

    assert result == {
        "status": "ok",
        "source": "Forward DNS Verification",
        "ip": "192.0.2.1",
        "confirmed_hostnames": [],
        "results": [
            {
                "hostname": "dns.example.test",
                "addresses": [],
                "matches_ip": False,
            }
        ],
        "error": None,
    }


def test_forward_dns_timeout_means_unavailable():
    import dns.exception

    from core.reverse_dns import verify_forward_dns

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.side_effect = (
            dns.exception.Timeout
        )

        result = verify_forward_dns(
            "192.0.2.1",
            ["dns.example.test"],
        )

    assert result == {
        "status": "unavailable",
        "source": "Forward DNS Verification",
        "ip": "192.0.2.1",
        "confirmed_hostnames": [],
        "results": [
            {
                "hostname": "dns.example.test",
                "addresses": [],
                "matches_ip": False,
                "error": "DNS timeout",
            }
        ],
        "error": "DNS timeout",
    }


def test_forward_dns_mixed_results_means_partial():
    import dns.exception

    from core.reverse_dns import verify_forward_dns

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.side_effect = [
            ["192.0.2.1"],
            dns.exception.Timeout,
        ]

        result = verify_forward_dns(
            "192.0.2.1",
            [
                "confirmed.example.test",
                "timeout.example.test",
            ],
        )

    assert result == {
        "status": "partial",
        "source": "Forward DNS Verification",
        "ip": "192.0.2.1",
        "confirmed_hostnames": [
            "confirmed.example.test",
        ],
        "results": [
            {
                "hostname": "confirmed.example.test",
                "addresses": [
                    "192.0.2.1",
                ],
                "matches_ip": True,
            },
            {
                "hostname": "timeout.example.test",
                "addresses": [],
                "matches_ip": False,
                "error": "DNS timeout",
            },
        ],
        "error": "DNS timeout",
    }


def test_forward_dns_without_hostnames_is_not_applicable():
    from core.reverse_dns import verify_forward_dns

    result = verify_forward_dns(
        "192.0.2.1",
        [],
    )

    assert result == {
        "status": "not_applicable",
        "source": "Forward DNS Verification",
        "ip": "192.0.2.1",
        "confirmed_hostnames": [],
        "results": [],
        "error": None,
    }


def test_forward_dns_no_nameservers_means_unavailable():
    import dns.resolver

    from core.reverse_dns import verify_forward_dns

    with patch(
        "core.reverse_dns.dns.resolver.resolve"
    ) as mock_resolve:
        mock_resolve.side_effect = (
            dns.resolver.NoNameservers
        )

        result = verify_forward_dns(
            "192.0.2.1",
            ["dns.example.test"],
        )

    assert result == {
        "status": "unavailable",
        "source": "Forward DNS Verification",
        "ip": "192.0.2.1",
        "confirmed_hostnames": [],
        "results": [
            {
                "hostname": "dns.example.test",
                "addresses": [],
                "matches_ip": False,
                "error": "DNS nameservers unavailable",
            }
        ],
        "error": "DNS nameservers unavailable",
    }
