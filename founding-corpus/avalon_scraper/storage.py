from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
import csv
import orjson
import pandas as pd
from .utils import slugify, content_hash

@dataclass
class DocMeta:
    url: str
    title: str
    collection: Optional[str]
    date_text: Optional[str]
    html_lang: Optional[str]
    retrieved_at: str
    parent_url: Optional[str]
    word_count: int
    char_count: int
    hash: str
    path: str


class Storage:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.docs_dir = out_dir / "docs"
        self.idx_csv = out_dir / "index.csv"
        self.idx_parquet = out_dir / "index.parquet"
        self.state_path = out_dir / "state.json"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        # init CSV header
        if not self.idx_csv.exists():
            with open(self.idx_csv, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([
                    "url","title","collection","date_text","html_lang","retrieved_at","parent_url",
                    "word_count","char_count","hash","path"
                ])

    def write_markdown(self, meta: DocMeta, text: str) -> Path:
        slug_base = slugify(meta.title or meta.url.rsplit("/",1)[-1])
        fname = f"{slug_base}.md"
        out_path = self.docs_dir / fname
        front = asdict(meta).copy()
        # YAML front-matter
        fm_lines = ["---"]
        for k, v in front.items():
            v_str = ("" if v is None else str(v)).replace("\n"," ")
            fm_lines.append(f"{k}: {v_str}")
        fm_lines.append("---\n")
        body = "\n".join(fm_lines) + text
        out_path.write_text(body, encoding="utf-8")
        return out_path

    def append_index(self, meta: DocMeta) -> None:
        with open(self.idx_csv, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                meta.url, meta.title, meta.collection, meta.date_text, meta.html_lang, meta.retrieved_at,
                meta.parent_url, meta.word_count, meta.char_count, meta.hash, meta.path
            ])

    def finalize_parquet(self) -> None:
        df = pd.read_csv(self.idx_csv)
        df.to_parquet(self.idx_parquet, index=False)

    # State management
    def load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            return orjson.loads(self.state_path.read_bytes())
        return {"visited": {}, "outputs": {}}

    def save_state(self, state: Dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_bytes(orjson.dumps(state))

    def mark_done(self, state: Dict[str, Any], url: str, out_path: Optional[Path]) -> None:
        state["visited"][url] = True
        if out_path:
            state["outputs"][url] = str(out_path)
        self.save_state(state)

    @staticmethod
    def compute_hash(text: str) -> str:
        return content_hash(text)