from __future__ import annotations
from typing import Dict, Any, Iterable, Tuple
import re
from collections import defaultdict

RE_HYPH = re.compile(r"([A-Za-z])-(\s*\n)([a-z])")
RE_PGNUM = re.compile(r"^\s*\d+\s*$")
RE_CTRL = re.compile(r"[\u0000-\u001F\u007F]")


def merge_hyphenations(text: str) -> str:
    return RE_HYPH.sub(r"\1\3", text)


def cleanup_page_text(text: str) -> str:
    # remove control chars
    text = RE_CTRL.sub(" ", text)
    # drop standalone page-number lines
    lines = [ln for ln in text.splitlines() if not RE_PGNUM.match(ln)]
    text = "\n".join(lines)
    text = merge_hyphenations(text)
    return text


def assemble_books(pages: Iterable[Dict[str, Any]]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    by_book: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"pages": [], "meta": None})
    for p in pages:
        rid = str(p.get("record_id"))
        cleaned = cleanup_page_text(p.get("text", ""))
        page = {
            "pg": p.get("pg"),
            "text": cleaned,
            "mean_wc_ocr": p.get("mean_wc_ocr")
        }
        if by_book[rid]["meta"] is None:
            by_book[rid]["meta"] = {
                "record_id": rid,
                "date": p.get("date"),
                "raw_date": p.get("raw_date"),
                "title": p.get("title"),
                "place": p.get("place")
            }
        by_book[rid]["pages"].append(page)
    # yield assembled
    for rid, bundle in by_book.items():
        pages_sorted = sorted(bundle["pages"], key=lambda x: (x["pg"] if isinstance(x["pg"], int) else 1e12))
        texts = [pg["text"].strip() for pg in pages_sorted if pg["text"].strip()]
        full = "\n\n".join(texts)
        wc = len(full.split()); cc = len(full)
        kept_pages = len(texts)
        mwc = 0.0
        vals = [pg.get("mean_wc_ocr") for pg in pages_sorted if isinstance(pg.get("mean_wc_ocr"), (int,float))]
        if vals:
            mwc = sum(vals)/len(vals)
        meta = bundle["meta"]
        doc = {
            **meta,
            "page_count": kept_pages,
            "mean_wc_ocr_book": mwc,
            "word_count": wc,
            "char_count": cc,
            "text": full
        }
        yield rid, doc