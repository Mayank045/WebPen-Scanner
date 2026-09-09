from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

from app.scanner.recon import ReconError, _request_target


MAX_PAGES = 25
MAX_DEPTH = 2
REQUEST_TIMEOUT = 10
SUPPORTED_SCHEMES = {"http", "https"}
IGNORED_EXTENSIONS = {
    ".7z", ".avi", ".bin", ".bmp", ".css", ".csv", ".doc", ".docx",
    ".gif", ".gz", ".ico", ".jpeg", ".jpg", ".js", ".mp3", ".mp4",
    ".pdf", ".png", ".svg",     ".tar", ".webp", ".wav", ".webm", ".woff",
    ".woff2", ".xls", ".xlsx", ".zip",
}


def normalize_crawl_url(url, base_url=None):
    candidate = urljoin(base_url, url) if base_url else url
    candidate, _ = urldefrag(candidate)
    parsed = urlparse(candidate)
    if parsed.scheme not in SUPPORTED_SCHEMES or not parsed.hostname:
        return None
    if parsed.username or parsed.password:
        return None
    path = parsed.path or "/"
    return urlunparse((parsed.scheme, parsed.netloc.lower(), path, "", parsed.query, ""))


def _same_scope(url, scope):
    parsed = urlparse(url)
    return (
        parsed.scheme == scope.scheme
        and parsed.hostname == scope.hostname
        and parsed.port == scope.port
    )


def _is_html(response):
    content_type = response.headers.get("Content-Type", "").lower()
    return "text/html" in content_type or "application/xhtml+xml" in content_type


def crawl_site(start_url):
    start = normalize_crawl_url(start_url)
    if not start:
        raise ReconError("The crawler start URL is invalid.")

    scope = urlparse(start)
    queue = deque([(start, 0)])
    queued = {start}
    pages = []
    discovered = []
    skipped = []
    limit_reached = False

    while queue:
        if len(pages) >= MAX_PAGES:
            limit_reached = True
            break
        current_url, depth = queue.popleft()
        try:
            response, body, _ = _request_target(
                current_url,
                timeout=REQUEST_TIMEOUT,
                redirect_validator=lambda url: _same_scope(url, scope),
            )
        except ReconError as error:
            skipped.append({"url": current_url, "reason": str(error)})
            continue

        if not _is_html(response):
            skipped.append({"url": current_url, "reason": "non-html response"})
            continue

        content_type = response.headers.get("Content-Type", "")
        final_url = normalize_crawl_url(response.url)
        if not final_url or not _same_scope(final_url, scope):
            skipped.append({"url": current_url, "reason": "redirect left allowed scope"})
            continue

        soup = BeautifulSoup(body.decode(response.encoding or "utf-8", errors="replace"), "html.parser")
        links = []
        for anchor in soup.find_all("a", href=True):
            normalized = normalize_crawl_url(anchor["href"], final_url)
            if not normalized:
                continue
            links.append(normalized)
            if not _same_scope(normalized, scope):
                skipped.append({"url": normalized, "reason": "outside target scope"})
                continue
            if any(normalized.lower().split("?", 1)[0].endswith(ext.lower()) for ext in IGNORED_EXTENSIONS):
                skipped.append({"url": normalized, "reason": "non-page resource"})
                continue
            if depth < MAX_DEPTH and normalized not in queued:
                queued.add(normalized)
                queue.append((normalized, depth + 1))
                discovered.append(normalized)

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        pages.append({
            "url": final_url,
            "status_code": response.status_code,
            "content_type": content_type,
            "depth": depth,
            "title": title,
            "links_found": sorted(set(links)),
        })

    return {
        "start_url": start,
        "pages": pages,
        "discovered_urls": sorted(set(discovered)),
        "pages_crawled": len(pages),
        "max_depth": MAX_DEPTH,
        "limit_reached": limit_reached,
        "skipped": skipped,
    }
