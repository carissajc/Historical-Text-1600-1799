from __future__ import annotations
from typing import Iterable, Dict, Any, Generator, List
from pathlib import Path
from datasets import load_dataset
from .logtxt import log

FIELDS_KEEP = [
    "record_id","date","raw_date","title","place","pg","text","empty_pg",
    "Language_1","Language_2","Language_3","Language_4","mean_wc_ocr"
]


def lang_is_english(rec: Dict[str, Any], wanted: List[str]) -> bool:
    wl = {w.lower() for w in wanted}
    for k in ["Language_1","Language_2","Language_3","Language_4"]:
        v = rec.get(k)
        if isinstance(v, str) and v.lower() in wl:
            return True
    return False


def page_ok(rec: Dict[str, Any], year_min: int, year_max: int, languages: List[str], skip_empty_pages: bool) -> bool:
    if not lang_is_english(rec, languages):
        return False
    d = rec.get("date")
    try:
        # Handle both datetime objects and string/int dates
        if hasattr(d, 'year'):
            d = d.year
        else:
            d = int(d)
    except Exception:
        return False
    if not (year_min <= d <= year_max):
        return False
    t = rec.get("text") or ""
    if not isinstance(t, str) or not t.strip():
        return False
    if skip_empty_pages and rec.get("empty_pg") is True:
        return False
    return True


def stream_pages_direct(config_name: str, out_dir: Path, skip_empty_pages: bool, **filters) -> Generator[Dict[str, Any], None, None]:
    log(out_dir, "Loading via datasets with trust_remote_code=true (official BL dataset).")
    ds = load_dataset("TheBritishLibrary/blbooks", name=config_name, split="train", streaming=True, trust_remote_code=True)
    for rec in ds:
        if page_ok(rec, **filters, skip_empty_pages=skip_empty_pages):
            yield {k: rec.get(k) for k in FIELDS_KEEP}


def stream_pages_parquet(parquet_dir: Path, out_dir: Path, skip_empty_pages: bool, **filters) -> Generator[Dict[str, Any], None, None]:
    log(out_dir, f"Loading from Parquet at {parquet_dir} (safe convert mode).")
    ds = load_dataset("parquet", data_files=str(parquet_dir/"*.parquet"), split="train", streaming=True)
    for rec in ds:
        if page_ok(rec, **filters, skip_empty_pages=skip_empty_pages):
            yield {k: rec.get(k) for k in FIELDS_KEEP}