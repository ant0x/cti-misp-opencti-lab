from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse, urlunparse

from .models import Observable, ObservableType

DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$",
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "msclkid"}


def normalize_observable(
    raw: str,
    *,
    explicit_type: str | None = None,
    source: str = "manual",
    confidence: int = 50,
    tlp: str = "TLP:CLEAR",
    tags: list[str] | tuple[str, ...] | None = None,
) -> Observable | None:
    value = raw.strip().strip("\"'").strip()
    if not value or value.startswith("#"):
        return None

    obs_type = _coerce_type(explicit_type) if explicit_type else detect_type(value)
    normalized = normalize_value(value, obs_type)
    return Observable(
        value=normalized,
        type=obs_type,
        source=source or "manual",
        confidence=max(0, min(int(confidence), 100)),
        tlp=(tlp or "TLP:CLEAR").upper(),
        tags=tuple(tag.strip() for tag in (tags or []) if tag and tag.strip()),
    )


def detect_type(value: str) -> ObservableType:
    candidate = value.lower().rstrip(".")
    if _looks_like_url(value):
        return "url"
    try:
        ip = ipaddress.ip_address(candidate)
        return "ipv4" if ip.version == 4 else "ipv6"
    except ValueError:
        pass
    hash_candidate = candidate.replace(":", "")
    if len(hash_candidate) == 32 and _is_hex(hash_candidate):
        return "md5"
    if len(hash_candidate) == 40 and _is_hex(hash_candidate):
        return "sha1"
    if len(hash_candidate) == 64 and _is_hex(hash_candidate):
        return "sha256"
    if EMAIL_RE.match(candidate):
        return "email"
    if DOMAIN_RE.match(candidate):
        return "domain"
    return "unknown"


def normalize_value(value: str, obs_type: ObservableType) -> str:
    if obs_type == "url":
        return normalize_url(value)
    if obs_type in {"domain", "email"}:
        return value.lower().rstrip(".")
    if obs_type in {"md5", "sha1", "sha256"}:
        return value.lower().replace(":", "")
    if obs_type in {"ipv4", "ipv6"}:
        return str(ipaddress.ip_address(value.strip()))
    return value.strip()


def normalize_url(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    query_pairs = []
    for part in parsed.query.split("&"):
        if not part:
            continue
        key = part.split("=", 1)[0].lower()
        if key in TRACKING_QUERY_KEYS or key.startswith(TRACKING_QUERY_PREFIXES):
            continue
        query_pairs.append(part)
    return urlunparse((scheme, netloc, path, "", "&".join(query_pairs), ""))


def _coerce_type(value: str | None) -> ObservableType:
    normalized = (value or "").lower().replace("-", "").replace("_", "")
    aliases = {
        "ip": "ipv4",
        "ipv4": "ipv4",
        "ipv6": "ipv6",
        "domain": "domain",
        "hostname": "domain",
        "url": "url",
        "uri": "url",
        "md5": "md5",
        "sha1": "sha1",
        "sha256": "sha256",
        "email": "email",
        "mail": "email",
    }
    return aliases.get(normalized, "unknown")  # type: ignore[return-value]


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc and "/" in value)


def _is_hex(value: str) -> bool:
    return all(ch in "0123456789abcdef" for ch in value)

