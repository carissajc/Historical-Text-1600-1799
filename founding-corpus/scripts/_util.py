import os, time, json, orjson, re, yaml, unicodedata
from datetime import datetime
from pathlib import Path
from typing import Iterable
import requests
from requests.adapters import HTTPAdapter, Retry

def load_years(path): 
    y = yaml.safe_load(open(path, 'r'))
    return y["start"], y["end"]

def in_range(dt, start, end):
    try:
        d = datetime.fromisoformat(dt[:10])
        return datetime.fromisoformat(start) <= d <= datetime.fromisoformat(end)
    except Exception:
        return False

def session():
    s = requests.Session()
    r = Retry(total=5, backoff_factor=0.5, status_forcelist=[429,500,502,503,504])
    s.mount("https://", HTTPAdapter(max_retries=r))
    return s

def write_jsonl(path, recs: Iterable[dict]):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(orjson.dumps(r).decode("utf-8") + "\n")

def clean_text_basic(t: str) -> str:
    t = unicodedata.normalize("NFKC", t)
    t = t.replace("\u00AD", "")  # soft hyphen
    t = re.sub(r"-\n(?=\w)", "", t)  # de-hyphen linebreak
    t = re.sub(r"\s+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t.strip()
