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
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


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


def _hostname_is_blocked(hostname: str) -> bool:
    normalized = hostname.strip().lower().rstrip(".")
    if not normalized or normalized == "localhost" or normalized.endswith(".localhost"):
        return True
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        return False
    return _ip_is_blocked(address)


def _ip_is_blocked(address: ipaddress._BaseAddress) -> bool:
    if str(address) == "169.254.169.254":
        return True
    return any(
        [
            address.is_private,
            address.is_loopback,
            address.is_link_local,
            address.is_multicast,
            address.is_reserved,
            address.is_unspecified,
        ]
    )


def _resolve_host_ips(hostname: str, port: int | None) -> Iterable[ipaddress._BaseAddress]:
    infos = socket.getaddrinfo(hostname, port or 443, type=socket.SOCK_STREAM)
    for info in infos:
        raw = info[4][0]
        yield ipaddress.ip_address(raw)


def validate_public_url(url: str) -> str:
    parsed = urlparse(str(url or "").strip())
    if parsed.scheme.lower() not in {"http", "https"}:
        raise URLSourceImportError("url_security_blocked", "URL must use http or https.")
    hostname = parsed.hostname or ""
    if _hostname_is_blocked(hostname):
        raise URLSourceImportError("url_security_blocked", "URL host is not allowed.")
    try:
        addresses = list(_resolve_host_ips(hostname, parsed.port))
    except (OSError, ValueError) as exc:
        raise URLSourceImportError("unsupported_site", "URL host could not be resolved.") from exc
    if not addresses or any(_ip_is_blocked(address) for address in addresses):
        raise URLSourceImportError("url_security_blocked", "URL resolves to a blocked network address.")
    return parsed.geturl()


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
            if exc.code in {401, 403, 451}:
                raise URLSourceImportError("robots_or_permission_blocked", "URL is blocked by permission or policy.") from exc
            raise URLSourceImportError("extraction_failed", f"URL fetch failed with HTTP {exc.code}.") from exc
        except TimeoutError as exc:
            raise URLSourceImportError("fetch_timeout", "URL fetch timed out.") from exc
        except URLError as exc:
            reason = getattr(exc, "reason", None)
            if isinstance(reason, TimeoutError):
                raise URLSourceImportError("fetch_timeout", "URL fetch timed out.") from exc
            raise URLSourceImportError("unsupported_site", "URL could not be fetched.") from exc
        break

    content_type = response.headers.get("Content-Type", "text/html")
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type not in {"text/html", "text/plain", "application/xhtml+xml"}:
        raise URLSourceImportError("unsupported_site", f"Unsupported content type: {media_type or 'unknown'}.")
    raw = response.read(max_response_size + 1)
    if len(raw) > max_response_size:
        raise URLSourceImportError("extraction_failed", "URL response is larger than max_response_size.")
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
