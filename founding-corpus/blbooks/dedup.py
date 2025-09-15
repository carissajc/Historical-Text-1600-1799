from __future__ import annotations
from typing import List, Dict, Any, Tuple
import re
import xxhash
from datasketch import MinHash, MinHashLSH

RE_WS = re.compile(r"\s+")


def norm_text(t: str) -> str:
    return RE_WS.sub(" ", t.strip())


def shingles(s: str, k: int = 5) -> List[str]:
    return [s[i:i+k] for i in range(0, max(len(s)-k+1, 0))]


def mhash(s: str, num_perm: int = 64) -> MinHash:
    m = MinHash(num_perm=num_perm)
    for g in set(shingles(s, 5)):
        m.update(g.encode("utf-8"))
    return m


def deduplicate(docs: List[Dict[str, Any]], near_thresh: float = 0.8) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    # exact
    seen_hash = {}
    exact_dropped = 0
    exact_kept: List[Dict[str, Any]] = []
    for d in docs:
        t = norm_text(d["text"]) 
        h = xxhash.xxh64(t.encode("utf-8")).hexdigest()
        d["doc_id"] = h
        if h in seen_hash:
            exact_dropped += 1
            continue
        seen_hash[h] = True
        exact_kept.append(d)
    # near dup via LSH
    lsh = MinHashLSH(threshold=near_thresh, num_perm=64)
    kept: List[Dict[str, Any]] = []
    near_dropped = 0
    for d in exact_kept:
        t = norm_text(d["text"])[:100000]
        mh = mhash(t)
        near = lsh.query(mh)
        if near:
            # choose by mean_wc_ocr_book then length
            rival = next((x for x in kept if x["doc_id"] in near), None)
            if rival:
                choose_new = (d.get("mean_wc_ocr_book", 0) > rival.get("mean_wc_ocr_book", 0)) or (d.get("word_count", 0) > rival.get("word_count", 0))
                if choose_new:
                    kept = [x for x in kept if x["doc_id"] not in near]
                    kept.append(d)
                else:
                    near_dropped += 1
            else:
                near_dropped += 1
        else:
            lsh.insert(d["doc_id"], mh)
            kept.append(d)
    report = {"input": len(docs), "after_exact": len(exact_kept), "exact_dropped": exact_dropped, "after_near": len(kept), "near_dropped": near_dropped}
    return kept, report