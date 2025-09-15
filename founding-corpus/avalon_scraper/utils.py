from __future__ import annotations
import re
import urllib.parse as up
from datetime import datetime, timezone
import xxhash

BASE = "https://avalon.law.yale.edu/"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_url(url: str, parent: str | None = None) -> str:
    url = url.strip()
    if parent:
        url = up.urljoin(parent, url)
    # strip fragments, normalize path
    parts = up.urlsplit(url)
    path = re.sub(r"/+", "/", parts.path)
    norm = up.urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))
    return norm


def is_same_site(url: str) -> bool:
    return url.startswith(BASE)


def slugify(text: str, max_len: int = 120) -> str:
    text = re.sub(r"[\s_]+", "-", text.strip())
    text = re.sub(r"[^a-zA-Z0-9\-]", "", text)
    text = re.sub(r"-+", "-", text)
    return text[:max_len].strip("-") or "doc"


def content_hash(text: str) -> str:
    return xxhash.xxh64(text.encode("utf-8")).hexdigest()