"""Public URL source extraction contract for target workspace imports."""

from __future__ import annotations

import html
import ipaddress
import socket
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


class URLSourceImportError(ValueError):
    def __init__(self, code: str, message: str, *, block_reason: str | None = None, status_code: int | None = None):
        super().__init__(message)
        self.code = code
        self.block_reason = block_reason or _default_block_reason(code)
        self.status_code = status_code or _default_status_code(self.block_reason)


@dataclass(frozen=True)
class URLSourceText:
    url: str
    final_url: str
    title: str
    content: str
    content_type: str
    fetched_at: str


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401, ANN001
        return None


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._in_title = False
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):  # noqa: ANN001
        normalized = tag.lower()
        if normalized in {"script", "style", "noscript", "template", "svg", "canvas"}:
            self._skip_depth += 1
        if normalized == "title":
            self._in_title = True
        if normalized in {"p", "div", "section", "article", "li", "br", "h1", "h2", "h3", "h4"}:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str):
        normalized = tag.lower()
        if normalized in {"script", "style", "noscript", "template", "svg", "canvas"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if normalized == "title":
            self._in_title = False
        if normalized in {"p", "div", "section", "article", "li", "h1", "h2", "h3", "h4"}:
            self.text_parts.append("\n")

    def handle_data(self, data: str):
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
            return
        if self._skip_depth:
            return
        self.text_parts.append(text)


def _collapse_text(value: str) -> str:
    lines = []
    for line in value.replace("\r", "\n").split("\n"):
        collapsed = " ".join(line.split())
        if collapsed:
            lines.append(collapsed)
    return "\n".join(lines).strip()


def _default_block_reason(code: str) -> str:
    return {
        "url_security_blocked": "ssrf",
        "private_ip_blocked": "private_ip",
        "fetch_timeout": "timeout",
        "unsupported_content_type": "unsupported_content_type",
        "robots_or_permission_blocked": "permission_denied",
        "paywall": "paywall",
    }.get(code, "ssrf")


def _default_status_code(block_reason: str) -> int:
    return {
        "ssrf": 400,
        "private_ip": 400,
        "timeout": 408,
        "unsupported_content_type": 415,
        "robots_blocked": 403,
        "permission_denied": 403,
        "paywall": 402,
    }.get(block_reason, 400)


def _hostname_block_reason(hostname: str) -> str | None:
    normalized = hostname.strip().lower().rstrip(".")
    if not normalized or normalized == "localhost" or normalized.endswith(".localhost"):
        return "ssrf"
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        return None
    return _ip_block_reason(address)


def _ip_block_reason(address: ipaddress._BaseAddress) -> str | None:
    if str(address) == "169.254.169.254":
        return "ssrf"
    if address.is_loopback or address.is_link_local or address.is_multicast or address.is_reserved or address.is_unspecified:
        return "ssrf"
    if address.is_private:
        text = str(address)
        if text.startswith("10."):
            return "ssrf"
        return "private_ip"
    return None


def _resolve_host_ips(hostname: str, port: int | None) -> Iterable[ipaddress._BaseAddress]:
    infos = socket.getaddrinfo(hostname, port or 443, type=socket.SOCK_STREAM)
    for info in infos:
        raw = info[4][0]
        yield ipaddress.ip_address(raw)


def validate_public_url(url: str) -> str:
    parsed = urlparse(str(url or "").strip())
    if parsed.scheme.lower() not in {"http", "https"}:
        raise URLSourceImportError("url_security_blocked", "URL must use http or https.", block_reason="ssrf")
    hostname = parsed.hostname or ""
    host_reason = _hostname_block_reason(hostname)
    if host_reason:
        raise URLSourceImportError(_block_code(host_reason), "URL host is not allowed.", block_reason=host_reason)
    try:
        addresses = list(_resolve_host_ips(hostname, parsed.port))
    except (OSError, ValueError) as exc:
        raise URLSourceImportError("permission_denied", "URL host could not be resolved.", block_reason="permission_denied") from exc
    blocked_reasons = [reason for address in addresses if (reason := _ip_block_reason(address))]
    if not addresses or blocked_reasons:
        reason = "ssrf" if "ssrf" in blocked_reasons else "private_ip"
        raise URLSourceImportError(_block_code(reason), "URL resolves to a blocked network address.", block_reason=reason)
    return parsed.geturl()


def _block_code(block_reason: str) -> str:
    return {
        "private_ip": "private_ip_blocked",
        "timeout": "timeout",
        "unsupported_content_type": "unsupported_content_type",
        "robots_blocked": "robots_blocked",
        "permission_denied": "permission_denied",
        "paywall": "paywall",
    }.get(block_reason, "ssrf_blocked")


def _extract_text(raw: bytes, *, content_type: str, fallback_title: str) -> tuple[str, str]:
    charset = "utf-8"
    for part in content_type.split(";"):
        key, _, value = part.strip().partition("=")
        if key.lower() == "charset" and value:
            charset = value.strip()
    decoded = raw.decode(charset, errors="replace")
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type == "text/plain":
        text = _collapse_text(decoded)
        return fallback_title, text
    parser = _HTMLTextExtractor()
    parser.feed(decoded)
    parser.close()
    title = _collapse_text(" ".join(parser.title_parts)) or fallback_title
    text = _collapse_text("\n".join(parser.text_parts))
    return title, html.unescape(text)


def fetch_url_source_text(
    url: str,
    *,
    title: str | None = None,
    timeout_seconds: float = 8.0,
    max_response_size: int = 1_000_000,
    redirect_limit: int = 4,
) -> URLSourceText:
    current_url = validate_public_url(url)
    opener = build_opener(_NoRedirectHandler)
    redirects = 0
    while True:
        request = Request(
            current_url,
            headers={
                "User-Agent": "ResearchNotebookURLExtractor/1.0",
                "Accept": "text/html,text/plain,application/xhtml+xml;q=0.9,*/*;q=0.1",
            },
            method="GET",
        )
        try:
            response = opener.open(request, timeout=timeout_seconds)
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                location = exc.headers.get("Location")
                if not location:
                    raise URLSourceImportError("extraction_failed", "Redirect response is missing Location.") from exc
                redirects += 1
                if redirects > redirect_limit:
                    raise URLSourceImportError("extraction_failed", "URL exceeded redirect limit.") from exc
                current_url = validate_public_url(urljoin(current_url, location))
                continue
            if exc.code == 402:
                raise URLSourceImportError("paywall", "URL requires paid access.", block_reason="paywall") from exc
            if exc.code == 451:
                raise URLSourceImportError("robots_blocked", "URL is blocked by policy.", block_reason="robots_blocked") from exc
            if exc.code in {401, 403}:
                raise URLSourceImportError("permission_denied", "URL is blocked by permission or policy.", block_reason="permission_denied") from exc
            raise URLSourceImportError("permission_denied", f"URL fetch failed with HTTP {exc.code}.", block_reason="permission_denied") from exc
        except TimeoutError as exc:
            raise URLSourceImportError("timeout", "URL fetch timed out.", block_reason="timeout") from exc
        except URLError as exc:
            reason = getattr(exc, "reason", None)
            if isinstance(reason, TimeoutError):
                raise URLSourceImportError("timeout", "URL fetch timed out.", block_reason="timeout") from exc
            raise URLSourceImportError("permission_denied", "URL could not be fetched.", block_reason="permission_denied") from exc
        break

    content_type = response.headers.get("Content-Type", "text/html")
    media_type = content_type.split(";", 1)[0].strip().lower()
    if not (media_type.startswith("text/") or media_type in {"application/xhtml+xml", "application/pdf"}):
        raise URLSourceImportError("unsupported_content_type", f"Unsupported content type: {media_type or 'unknown'}.", block_reason="unsupported_content_type")
    if media_type == "application/pdf":
        raise URLSourceImportError("ocr_required", "URL PDF extraction requires OCR or PDF ingestion support.", block_reason="unsupported_content_type")
    raw = response.read(max_response_size + 1)
    if len(raw) > max_response_size:
        raise URLSourceImportError("unsupported_content_type", "URL response is larger than max_response_size.", block_reason="unsupported_content_type")
    extracted_title, extracted_text = _extract_text(raw, content_type=content_type, fallback_title=title or current_url)
    if not extracted_text:
        raise URLSourceImportError("extraction_failed", "No readable text was extracted from URL.")
    content = f"# {extracted_title}\n\nSource URL: {current_url}\n\n{extracted_text}"
    return URLSourceText(
        url=url,
        final_url=current_url,
        title=title or extracted_title,
        content=content,
        content_type=media_type,
        fetched_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
