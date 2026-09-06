import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


SEVERITY_WEIGHTS = {"low": 10, "medium": 25, "high": 40, "critical": 60}
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_REDIRECTS = 5


class ReconError(Exception):
    """Expected, user-facing errors raised during basic reconnaissance."""


def _resolve_public_ip(hostname, port):
    try:
        addresses = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except OSError as error:
        raise ReconError(f"Could not resolve hostname '{hostname}'.") from error

    for address in addresses:
        candidate = address[4][0]
        parsed_address = ipaddress.ip_address(candidate)
        if not (
            parsed_address.is_private
            or parsed_address.is_loopback
            or parsed_address.is_link_local
            or parsed_address.is_multicast
            or parsed_address.is_unspecified
            or parsed_address.is_reserved
        ):
            return candidate
    raise ReconError("The target resolves to a non-public network address.")


def _request_target(url, timeout=10):
    current_url = url
    session = requests.Session()
    for _ in range(MAX_REDIRECTS + 1):
        parsed = urlparse(current_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ReconError("The target redirect used an unsupported URL.")
        ip_address = _resolve_public_ip(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
        try:
            response = session.get(
                current_url,
                timeout=timeout,
                allow_redirects=False,
                stream=True,
            )
        except requests.RequestException as error:
            raise ReconError("The target could not be reached.") from error

        if response.is_redirect:
            location = response.headers.get("Location")
            response.close()
            if not location:
                raise ReconError("The target returned an invalid redirect.")
            current_url = urljoin(current_url, location)
            continue

        try:
            body = response.raw.read(MAX_RESPONSE_BYTES + 1)
        finally:
            response.close()
        return response, body[:MAX_RESPONSE_BYTES], ip_address

    raise ReconError("The target exceeded the redirect limit.")


def _safe_get(url, timeout=5):
    try:
        response, _, _ = _request_target(url, timeout=timeout)
        return response
    except ReconError:
        return None


def _collect_links(soup, base_url):
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag.get("href")
        if not href:
            continue
        try:
            absolute = urljoin(base_url, href)
        except Exception:
            continue
        links.append(absolute)
    return links[:25]


def _collect_forms(soup):
    forms = []
    for form in soup.find_all("form"):
        action = form.get("action") or ""
        method = (form.get("method") or "GET").upper()
        fields = []
        for field in form.find_all(["input", "textarea", "select"]):
            name = field.get("name") or ""
            field_type = field.name if field.name else "input"
            if name:
                fields.append({"name": name, "type": field_type})
        forms.append({"action": action, "method": method, "fields": fields})
    return forms[:10]


def _add_finding(findings, severity, title, evidence):
    findings.append({
        "severity": severity,
        "title": title,
        "evidence": evidence,
    })


def scan_target(target_url):
    parsed_target = urlparse(target_url)
    if not parsed_target.hostname:
        raise ReconError("The target does not contain a valid hostname.")
    ip_address = _resolve_public_ip(
        parsed_target.hostname,
        parsed_target.port or (443 if parsed_target.scheme == "https" else 80),
    )
    response, body, final_ip_address = _request_target(target_url)

    parsed = urlparse(response.url)
    encoding = response.encoding or "utf-8"
    body_text = body.decode(encoding, errors="replace")
    soup = BeautifulSoup(body_text, "html.parser") if body_text else None
    title = ""
    if soup and soup.title and soup.title.string:
        title = soup.title.string.strip()

    findings = []
    headers = {key: value for key, value in response.headers.items()}

    required_headers = [
        "Server",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Content-Security-Policy",
    ]
    for header_name in required_headers:
        if not response.headers.get(header_name):
            _add_finding(findings, "medium", f"Missing security header: {header_name}", f"The response did not include the {header_name} header.")

    if parsed.scheme == "https" and not response.headers.get("Strict-Transport-Security"):
        _add_finding(findings, "medium", "HSTS is not enabled", "The site uses HTTPS but does not send a Strict-Transport-Security header.")

    if response.cookies:
        for cookie in response.cookies:
            cookie_flags = []
            if not cookie.secure:
                cookie_flags.append("Secure")
            if not cookie.has_nonstandard_attr("HttpOnly"):
                cookie_flags.append("HttpOnly")
            if cookie_flags:
                _add_finding(findings, "medium", "Cookie is missing secure attributes", f"The cookie '{cookie.name}' is missing: {', '.join(cookie_flags)}.")

    if response.status_code >= 500:
        _add_finding(findings, "low", "Server error encountered", f"The target returned HTTP {response.status_code}.")

    if response.status_code in {301, 302, 307, 308}:
        location = response.headers.get("Location")
        if location:
            if location.startswith("http://"):
                _add_finding(findings, "medium", "Potential redirect to insecure scheme", f"The target redirected to {location}, which uses HTTP.")

    if parsed.scheme == "http":
        _add_finding(findings, "medium", "Target is served over plain HTTP", "The URL uses HTTP. Prefer HTTPS to protect confidentiality and integrity.")

    sensitive_paths = ["/.git", "/.env", "/admin", "/backup.zip", "/config.php", "/phpinfo.php"]
    discovered_sensitive = []
    for item in sensitive_paths:
        candidate = urljoin(response.url, item)
        probe = _safe_get(candidate)
        if probe and probe.status_code < 400:
            discovered_sensitive.append(candidate)
    for candidate in discovered_sensitive:
        _add_finding(findings, "high", "Sensitive or exposed artifact discovered", f"The scanner found a reachable resource at {candidate}.")

    risk_score = 0
    for finding in findings:
        risk_score += SEVERITY_WEIGHTS.get(finding["severity"], 10)
    risk_score = min(risk_score, 100)

    summary = (
        f"Scan completed with {len(findings)} finding(s) and a risk score of {risk_score}. "
        f"The server responded with HTTP {response.status_code} and the page title was '{title or 'unknown'}'."
    )
    return {
        "target": {
            "url": target_url,
            "hostname": parsed_target.hostname,
            "scheme": parsed.scheme,
            "ip_address": final_ip_address or ip_address,
        },
        "http": {
            "status_code": response.status_code,
            "final_url": response.url,
            "headers": headers,
        },
        "scan": {
            "status": "completed",
            "summary": summary,
            "findings": findings,
            "risk_score": risk_score,
        },
    }
