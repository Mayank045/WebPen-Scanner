import re
from urllib.parse import urlparse


SEVERITY_WEIGHTS = {"low": 10, "medium": 25, "high": 40, "critical": 60}


def _finding(
    finding_id,
    severity,
    category,
    title,
    description,
    evidence,
    recommendation,
    affected_url,
    confidence="high",
):
    return {
        "id": finding_id,
        "severity": severity,
        "category": category,
        "title": title,
        "description": description,
        "evidence": evidence,
        "recommendation": recommendation,
        "affected_url": affected_url,
        "confidence": confidence,
    }


def _header_findings(http):
    headers = {key.lower(): value for key, value in http.get("headers", {}).items()}
    url = http.get("final_url")
    checks = (
        ("content-security-policy", "medium", "CSP is missing", "Content-Security-Policy is not present.", "Configure a restrictive Content-Security-Policy appropriate for the application."),
        ("x-frame-options", "medium", "Clickjacking protection is missing", "X-Frame-Options is not present.", "Set X-Frame-Options or use CSP frame-ancestors to control framing."),
        ("x-content-type-options", "low", "MIME sniffing protection is missing", "X-Content-Type-Options is not present.", "Set X-Content-Type-Options: nosniff."),
        ("strict-transport-security", "medium", "HSTS is missing", "Strict-Transport-Security is not present.", "Enable HSTS after confirming HTTPS is configured for the target."),
        ("referrer-policy", "low", "Referrer-Policy is missing", "Referrer-Policy is not present.", "Set a Referrer-Policy suitable for the application's privacy requirements."),
        ("permissions-policy", "low", "Permissions-Policy is missing", "Permissions-Policy is not present.", "Define a restrictive Permissions-Policy for browser features the application does not need."),
    )
    findings = []
    for header, severity, title, evidence, recommendation in checks:
        if not headers.get(header):
            findings.append(_finding(
                f"header-missing-{header}",
                severity,
                "security-headers",
                title,
                f"The response does not advertise the {header} header.",
                evidence,
                recommendation,
                url,
            ))
    return findings


def _transport_findings(target, http, crawl):
    findings = []
    url = http.get("final_url") or target.get("url")
    scheme = target.get("scheme")
    headers = {key.lower(): value for key, value in http.get("headers", {}).items()}
    if scheme == "http":
        findings.append(_finding(
            "transport-plain-http",
            "medium",
            "transport",
            "Target uses plain HTTP",
            "The target URL does not use encrypted transport.",
            f"The target scheme is {scheme.upper()}.",
            "Prefer HTTPS and redirect HTTP traffic to HTTPS.",
            url,
        ))
    if scheme == "https" and not headers.get("strict-transport-security"):
        findings.append(_finding(
            "transport-hsts-missing",
            "medium",
            "transport",
            "HTTPS target lacks HSTS",
            "HTTPS is in use, but the response does not request strict HTTPS transport.",
            "Strict-Transport-Security was not present in the response headers.",
            "Enable HSTS after validating that all target subresources support HTTPS.",
            url,
        ))
    if scheme == "https":
        insecure_links = []
        for page in crawl.get("pages", []):
            insecure_links.extend(
                link for link in page.get("links_found", [])
                if urlparse(link).scheme == "http"
            )
        if insecure_links:
            findings.append(_finding(
                "transport-insecure-links",
                "medium",
                "transport",
                "HTTPS page references HTTP links",
                "A crawled HTTPS page references one or more insecure HTTP URLs.",
                ", ".join(sorted(set(insecure_links))[:5]),
                "Update links and resources to use HTTPS.",
                url,
                "medium",
            ))
    return findings


def _cookie_findings(http):
    findings = []
    url = http.get("final_url")
    for cookie in http.get("cookies", []):
        missing = []
        if not cookie.get("secure"):
            missing.append("Secure")
        if not cookie.get("httponly"):
            missing.append("HttpOnly")
        if not cookie.get("samesite"):
            missing.append("SameSite")
        if missing:
            findings.append(_finding(
                f"cookie-attributes-{cookie.get('name', 'unknown')}",
                "medium",
                "cookies",
                "Cookie is missing security attributes",
                "A received cookie does not include all recommended browser protections.",
                f"Cookie '{cookie.get('name', 'unknown')}' is missing: {', '.join(missing)}.",
                "Set Secure, HttpOnly, and an appropriate SameSite attribute without exposing cookie values.",
                url,
            ))
    return findings


def _cors_findings(http):
    headers = {key.lower(): value for key, value in http.get("headers", {}).items()}
    origin = headers.get("access-control-allow-origin", "").strip()
    credentials = headers.get("access-control-allow-credentials", "").strip().lower()
    if origin == "*":
        severity = "high" if credentials == "true" else "medium"
        return [_finding(
            "cors-wildcard-origin",
            severity,
            "cors",
            "CORS allows every origin",
            "The response permits cross-origin requests from any origin.",
            f"Access-Control-Allow-Origin: {origin}" + (f"; Access-Control-Allow-Credentials: {credentials}" if credentials else ""),
            "Restrict allowed origins to trusted origins and avoid combining wildcard origins with credentials.",
            http.get("final_url"),
        )]
    return []


def _disclosure_findings(http):
    headers = {key.lower(): value for key, value in http.get("headers", {}).items()}
    findings = []
    for header in ("server", "x-powered-by"):
        value = headers.get(header, "")
        if value and re.search(r"\d", value):
            findings.append(_finding(
                f"disclosure-{header}",
                "low",
                "information-disclosure",
                "Response header discloses version information",
                "A response header reveals implementation or version details.",
                f"{header}: {value}",
                "Remove unnecessary product and version details from public response headers.",
                http.get("final_url"),
                "medium",
            ))
    return findings


def run_passive_checks(target, http, crawl=None):
    crawl = crawl or {}
    findings = []
    for check in (
        _header_findings(http),
        _transport_findings(target, http, crawl),
        _cookie_findings(http),
        _cors_findings(http),
        _disclosure_findings(http),
    ):
        findings.extend(check)

    unique = {}
    for finding in findings:
        unique[finding["id"]] = finding
    return list(unique.values())


def calculate_risk_score(findings):
    return min(sum(SEVERITY_WEIGHTS.get(finding.get("severity"), 10) for finding in findings), 100)
