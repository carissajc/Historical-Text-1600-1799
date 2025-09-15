from __future__ import annotations
from pathlib import Path
from typing import Any
import orjson
from .utils import utc_now_iso

class HumanLogger:
    def __init__(self, out_dir: Path):
        self.log_path = out_dir / "LOG.txt"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, line: str) -> None:
        msg = f"[{utc_now_iso()}] {line.strip()}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(msg)


def write_structured(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "ab") as f:
        f.write(orjson.dumps(record) + b"\n")