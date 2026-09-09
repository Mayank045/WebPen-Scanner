import json
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from app.database import get_db
from app.scanner.crawler import crawl_site
from app.scanner.recon import ReconError, scan_target
from app.scanner.security_checks import calculate_risk_score, run_passive_checks


def normalize_url(target):
    value = target.strip()
    if "//" not in value and "://" not in value:
        value = "https://" + value
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https targets are supported.")
    if not parsed.hostname or any(character.isspace() for character in parsed.netloc):
        raise ValueError("A valid target URL is required.")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.query, parsed.fragment))


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def serialize_scan(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "target_url": row["target_url"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "summary": row["summary"],
        "risk_score": row["risk_score"],
        "findings": json.loads(row["findings"] or "[]"),
        "metadata": json.loads(row["metadata"] or "{}"),
    }


def create_scan_record(target):
    normalized = normalize_url(target)
    db = get_db()
    now = now_iso()
    cursor = db.execute(
        """
        INSERT INTO scans (target_url, status, created_at, updated_at, summary, findings, risk_score, metadata)
        VALUES (?, 'queued', ?, ?, 'Created and waiting to run.', '[]', 0, '{}')
        """,
        (normalized, now, now),
    )
    db.commit()
    scan_id = cursor.lastrowid
    return get_scan_by_id(scan_id)


def list_scans():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM scans ORDER BY created_at DESC"
    ).fetchall()
    return [serialize_scan(row) for row in rows]


def get_scan_by_id(scan_id):
    db = get_db()
    row = db.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
    return serialize_scan(row)


def run_scan(scan):
    db = get_db()
    now = now_iso()
    db.execute(
        "UPDATE scans SET status = 'running', updated_at = ? WHERE id = ?",
        (now, scan["id"]),
    )
    db.commit()

    target = scan["target_url"]
    try:
        result = scan_target(target)
    except ReconError as error:
        result = {
            "target": {
                "url": target,
                "hostname": urlsplit(target).hostname,
                "scheme": urlsplit(target).scheme,
                "ip_address": None,
            },
            "http": {
                "status_code": None,
                "final_url": target,
                "headers": {},
                "cookies": [],
            },
            "scan": {
                "status": "failed",
                "summary": str(error),
                "risk_score": 0,
                "findings": [],
            },
        }

    scan_info = result["scan"]
    metadata = {
        "target": result["target"],
        "http": result["http"],
    }
    if scan_info["status"] == "completed":
        try:
            metadata["crawl"] = crawl_site(result["http"]["final_url"])
        except ReconError as error:
            metadata["crawl"] = {
                "start_url": result["http"]["final_url"],
                "pages": [],
                "discovered_urls": [],
                "pages_crawled": 0,
                "max_depth": 0,
                "limit_reached": False,
                "skipped": [{"url": result["http"]["final_url"], "reason": str(error)}],
            }
    if scan_info["status"] == "completed":
        passive_findings = run_passive_checks(
            metadata["target"],
            metadata["http"],
            metadata.get("crawl"),
        )
        existing_by_id = {finding.get("id") for finding in scan_info["findings"] if finding.get("id")}
        existing_titles = {finding.get("title") for finding in scan_info["findings"]}
        for finding in passive_findings:
            legacy_duplicate = (
                finding["category"] == "security-headers"
                and any(title.startswith("Missing security header:") for title in existing_titles)
            ) or (
                finding["id"] == "transport-hsts-missing"
                and "HSTS is not enabled" in existing_titles
            ) or (
                finding["id"] == "transport-plain-http"
                and "Target is served over plain HTTP" in existing_titles
            ) or (
                finding["category"] == "cookies"
                and "Cookie is missing secure attributes" in existing_titles
            )
            if finding["id"] not in existing_by_id and finding["title"] not in existing_titles and not legacy_duplicate:
                scan_info["findings"].append(finding)
        scan_info["risk_score"] = calculate_risk_score(scan_info["findings"])
        scan_info["summary"] = (
            f"Scan completed with {len(scan_info['findings'])} finding(s) "
            f"and a risk score of {scan_info['risk_score']}."
        )

    db.execute(
        """
        UPDATE scans
        SET status = ?, summary = ?, findings = ?, risk_score = ?, metadata = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            scan_info["status"],
            scan_info["summary"],
            json.dumps(scan_info["findings"]),
            scan_info["risk_score"],
            json.dumps(metadata),
            now,
            scan["id"],
        ),
    )
    db.commit()

    return {"message": "Scan complete.", "scan": get_scan_by_id(scan["id"]) }
