from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import orjson, gzip


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_parquet_shard(records: List[Dict[str, Any]], out_path: Path) -> None:
    if not records:
        return
    df = pd.DataFrame.from_records(records)
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, out_path)


def write_jsonl_gz(records: List[Dict[str, Any]], out_path: Path) -> None:
    if not records:
        return
    with gzip.open(out_path, 'wb') as f:
        for r in records:
            f.write(orjson.dumps(r))
            f.write(b"\n")

