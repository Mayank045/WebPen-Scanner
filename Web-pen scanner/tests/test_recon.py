from unittest.mock import Mock, patch

import pytest

from app.scanner.recon import (
    MAX_REDIRECTS,
    ReconError,
    _resolve_public_ip,
    scan_target,
)
from app.services.scan_service import normalize_url


def fake_response(url="https://example.test/", status_code=200, headers=None, body=b"ok"):
    response = Mock()
    response.url = url
    response.status_code = status_code
    response.headers = headers or {"Content-Type": "text/plain", "Server": "test"}
    response.cookies = []
    response.encoding = "utf-8"
    response.is_redirect = status_code in {301, 302, 303, 307, 308}
    response.raw.read.return_value = body
    return response


def public_address(*_args, **_kwargs):
    return [(2, 1, 6, "", ("93.184.216.34", 0))]


def test_invalid_url_is_rejected():
    with pytest.raises(ValueError):
        normalize_url("ftp://example.test")


def test_scan_collects_target_and_http_information():
    response = fake_response(headers={"Content-Type": "text/plain", "Server": "test"})
    with patch("app.scanner.recon.socket.getaddrinfo", side_effect=public_address), patch(
        "app.scanner.recon.requests.Session.get", return_value=response
    ):
        result = scan_target("https://example.test")

    assert result["target"] == {
        "url": "https://example.test",
        "hostname": "example.test",
        "scheme": "https",
        "ip_address": "93.184.216.34",
    }
    assert result["http"]["status_code"] == 200
    assert result["http"]["headers"]["Server"] == "test"
    assert result["scan"]["status"] == "completed"
    response.close.assert_called()


@pytest.mark.parametrize("address", ["127.0.0.1", "10.0.0.1", "169.254.1.1"])
def test_non_public_addresses_are_rejected(address):
    with patch(
        "app.scanner.recon.socket.getaddrinfo",
        return_value=[(2, 1, 6, "", (address, 0))],
    ):
        with pytest.raises(ReconError, match="non-public"):
            _resolve_public_ip("example.test", 443)


def test_unresolvable_hostname_is_rejected():
    with patch("app.scanner.recon.socket.getaddrinfo", side_effect=OSError):
        with pytest.raises(ReconError):
            _resolve_public_ip("invalid.test", 443)


def test_redirects_are_followed_and_revalidated():
    first = fake_response("https://example.test/start", status_code=302, headers={"Location": "/final"})
    second = fake_response("https://example.test/final")
    not_found = fake_response(status_code=404)

    def response_for_url(url, **_kwargs):
        if url.endswith("/start"):
            return first
        if url.endswith("/final"):
            return second
        return not_found

    with patch("app.scanner.recon.socket.getaddrinfo", side_effect=public_address), patch(
        "app.scanner.recon.requests.Session.get", side_effect=response_for_url
    ):
        result = scan_target("https://example.test/start")

    assert result["http"]["final_url"] == "https://example.test/final"


def test_redirect_limit_is_enforced():
    redirect = fake_response(status_code=302, headers={"Location": "/next"})
    with patch("app.scanner.recon.socket.getaddrinfo", side_effect=public_address), patch(
        "app.scanner.recon.requests.Session.get", return_value=redirect
    ):
        with pytest.raises(ReconError, match="redirect limit"):
            scan_target("https://example.test")

    assert redirect.close.call_count == MAX_REDIRECTS + 1


def test_network_failure_is_safe():
    with patch("app.scanner.recon.socket.getaddrinfo", side_effect=OSError):
        with pytest.raises(ReconError):
            scan_target("https://invalid.test")
