from __future__ import annotations
from typing import Optional, Tuple
from bs4 import BeautifulSoup
try:
    import trafilatura
    from trafilatura.settings import use_config
except Exception:  # allow running without trafilatura
    trafilatura = None
    def use_config():
        return None
from pdfminer.high_level import extract_text as pdf_extract_text
from datetime import datetime, timezone
import re

CFG = use_config()
if CFG is not None:
    CFG.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")
    CFG.set("DEFAULT", "EXTRACTION_TECHNIQUE", "fast")


def extract_text_html(html: str) -> str:
    # Try trafilatura if available
    if trafilatura and CFG is not None:
        text = trafilatura.extract(html, config=CFG, include_comments=False, include_tables=False, output_format="txt")
        if text and len(text.strip()) > 200:
            return text.strip()
    # Fallback to BS4
    soup = BeautifulSoup(html, "lxml")
    # remove nav/sidebars
    for sel in ["nav", "header", "footer", "script", "style", "aside"]:
        for tag in soup.select(sel):
            tag.decompose()
    # headings to markdown-style
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        level = int(h.name[1])
        h.string = ("#"*level + " " + (h.get_text(" ").strip()))
    text_parts = [p.get_text(" ", strip=True) for p in soup.find_all(["h1","h2","h3","h4","h5","h6","p"]) if p.get_text(strip=True)]
    text = "\n\n".join(text_parts)
    return text.strip()


def extract_text_pdf(pdf_bytes: bytes) -> str:
    try:
        return pdf_extract_text(pdf_bytes)
    except Exception:
        return ""


def extract_meta_html(html: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    title = None
    h1 = soup.find("h1")
    if soup.title and soup.title.get_text(strip=True):
        title = soup.title.get_text(strip=True)
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)
    # collection from breadcrumbs or headers
    collection = None
    bc = soup.select_one(".breadcrumb, .breadcrumbs")
    if bc:
        collection = bc.get_text(" ", strip=True)
    # date text near title
    date_text = None
    if h1 and h1.find_next():
        nxt = h1.find_next()
        txt = nxt.get_text(" ", strip=True)
        if txt and re.search(r"\b(16|17|18|19)\d{2}\b", txt):
            date_text = txt
    html_lang = soup.html.get("lang") if soup.html else None
    return title, collection, date_text if date_text else None, html_lang