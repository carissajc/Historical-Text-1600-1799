from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone

def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()

def log(out_dir: Path, message: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "LOG.txt"
    with open(p, "a", encoding="utf-8") as f:
        f.write(f"[{_ts()}] {message}\n")