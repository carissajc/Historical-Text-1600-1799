#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json
from tqdm import tqdm

from .logtxt import log
from .bl_loader import stream_pages_direct, stream_pages_parquet
from .bl_assemble import assemble_books
from .dedup import deduplicate
from .storage import write_parquet_shards, write_corpus_text, write_manifest, fold_into_main


def cmd_convert(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    log(out, f"Converting BL dataset to Parquet for config={args.config_name} (safe mode)…")
    # Use datasets CLI via Python API (subprocess-free shortcut)
    from datasets.commands.convert_to_parquet import convert_to_parquet as convert
    convert(dataset="TheBritishLibrary/blbooks", name=args.config_name, split="train", output_dir=str(out))
    log(out, f"Conversion complete at {out}")


def cmd_run(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    log(out, f"Started: British Library Books ingestion (languages={args.languages}, years={args.year_min}-{args.year_max}).")

    languages = [s.strip() for s in (args.languages or "English").split(",")]
    filters = dict(year_min=args.year_min, year_max=args.year_max, languages=languages)

    # choose stream mode
    pages_iter = None
    if args.mode in ("direct", "auto"):
        try:
            pages_iter = stream_pages_direct(args.config_name, out, args.skip_empty_pages, **filters)
        except Exception as e:
            log(out, f"Direct load failed: {e}; will try convert mode.")
            pages_iter = None
    if pages_iter is None:
        # require conversion path
        parquet_dir = Path(args.convert_dir or (out/"parquet"))
        if not parquet_dir.exists():
            log(out, "No conversion found; please run convert or pass --convert_dir. Aborting.")
            return
        pages_iter = stream_pages_parquet(parquet_dir, out, args.skip_empty_pages, **filters)

    # Collect pages and assemble
    page_count = 0
    books: List[Dict[str, Any]] = []
    buffer: Dict[str, Dict[str, Any]] = {}
    for rid, doc in assemble_books(pages_iter):
        page_count += doc.get("page_count", 0)
        books.append(doc)
    log(out, f"Assembled {len(books)} books from {page_count} pages.")

    # Dedup
    kept, report = deduplicate(books, near_thresh=args.near_dup_thresh)
    (out/"dedup_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    dropped = report.get("input", 0) - report.get("after_near", 0)
    log(out, f"Removed duplicates: {dropped} total (exact+near). Kept {len(kept)} books.")

    # Write outputs
    subname = "blbooks_1730_1779_en"
    paths = write_parquet_shards(out, kept, sub="books", shard_size=args.shard_size_books, compression="snappy")
    log(out, f"Wrote {len(paths)} book-level Parquet shards.")
    if args.write_corpus:
        corpus_path = write_corpus_text(out, kept)
        log(out, f"Wrote corpus text for sampling: {corpus_path}.")

    # Manifest and summary
    total_words = sum([d.get("word_count", 0) for d in kept])
    manifest = {
        "source": "blbooks",
        "subset": "en_1730_1779",
        "counts_books": len(kept),
        "total_words": int(total_words),
        "date_range": [args.year_min, args.year_max],
        "languages": languages,
        "paths": [str(p) for p in paths]
    }
    write_manifest(out, manifest)

    # Fold into main corpus, if provided
    if args.main_corpus_dir:
        fold_into_main(out, Path(args.main_corpus_dir), subdir=subname, shard_paths=paths, summary=manifest)
        log(out, f"Merged into main corpus at {args.main_corpus_dir}; manifest updated.")

    log(out, "Finished BL books ingestion.")


def main():
    p = argparse.ArgumentParser(description="BL Books English 1730–1779 ingestion")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("convert")
    pc.add_argument("--out", required=True)
    pc.add_argument("--config_name", default="1700_1799")
    pc.add_argument("--skip_empty_pages", type=bool, default=True)
    pc.set_defaults(func=cmd_convert)

    pr = sub.add_parser("run")
    pr.add_argument("--mode", choices=["auto","direct","convert"], default="auto")
    pr.add_argument("--config_name", default="1700_1799")
    pr.add_argument("--year_min", type=int, default=1730)
    pr.add_argument("--year_max", type=int, default=1779)
    pr.add_argument("--languages", default="English")
    pr.add_argument("--skip_empty_pages", type=bool, default=True)
    pr.add_argument("--out", required=True)
    pr.add_argument("--convert_dir", default=None)
    pr.add_argument("--main_corpus_dir", default=None)
    pr.add_argument("--near_dup_thresh", type=float, default=0.8)
    pr.add_argument("--shard_size_books", type=int, default=1000)
    pr.add_argument("--write_corpus", type=bool, default=False)
    pr.set_defaults(func=cmd_run)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()