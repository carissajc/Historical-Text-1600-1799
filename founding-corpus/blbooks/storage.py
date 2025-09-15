from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import math
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from .logtxt import log


def write_parquet_shards(out_dir: Path, rows: List[Dict[str, Any]], sub: str, shard_size: int = 1000, compression: str = "snappy") -> List[Path]:
    target_dir = out_dir / sub
    target_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    if not rows:
        return paths
    total = len(rows)
    shards = math.ceil(total / shard_size)
    for i in range(shards):
        batch = rows[i*shard_size:(i+1)*shard_size]
        table = pa.Table.from_pylist(batch)
        path = target_dir / f"part-{i:05d}.parquet"
        pq.write_table(table, path, compression=compression)
        paths.append(path)
    return paths


def write_corpus_text(out_dir: Path, docs: List[Dict[str, Any]], name: str = "corpus.txt") -> Path:
    path = out_dir / name
    with open(path, "w", encoding="utf-8") as f:
        for d in docs:
            t = d.get("text", "").replace("\n", " ").strip()
            if t:
                f.write(t + "\n")
    return path


def write_manifest(out_dir: Path, manifest: Dict[str, Any]) -> Path:
    p = out_dir / "manifest.json"
    p.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return p


def fold_into_main(out_dir: Path, main_dir: Path, subdir: str, shard_paths: List[Path], summary: Dict[str, Any]) -> None:
    target = main_dir / "shards" / subdir
    target.mkdir(parents=True, exist_ok=True)
    for p in shard_paths:
        dest = target / p.name
        dest.write_bytes(p.read_bytes())
    # update manifest
    mpath = main_dir / "manifest.json"
    if mpath.exists():
        data = json.loads(mpath.read_text())
    else:
        data = {"sources": []}
    data["sources"].append(summary)
    mpath.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # append human log
    log(main_dir, f"Merged BL books subset into main corpus: {summary.get('counts_books', 0)} books, {summary.get('total_words', 0)} words.")