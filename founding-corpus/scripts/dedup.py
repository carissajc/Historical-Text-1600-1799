import argparse, glob, orjson, os, hashlib
from datasketch import MinHash, MinHashLSH
from pathlib import Path

def shingles(s, k=13):
    return {s[i:i+k] for i in range(0, max(len(s)-k+1, 0))}

def mhash(s, k=13, num_perm=64):
    m=MinHash(num_perm=num_perm)
    for g in shingles(s, k=k): m.update(g.encode('utf-8'))
    return m

def main(args):
    files = sorted(Path(args.in_).glob("*.jsonl"))
    lsh = MinHashLSH(threshold=0.8, num_perm=64)
    seen_ids=set(); kept=[]; dropped=[]
    seen_exact_hashes=set()
    # prefer permissive first
    pref = {"PublicDomain":0, "CC-BY-4.0":1, "CC-BY-NC":2}
    records=[]
    for fp in files:
        for line in open(fp, encoding="utf-8"):
            r = orjson.loads(line); records.append(r)
    records.sort(key=lambda r: (pref.get(r["license_tag"],9), len(r["text"])*-1))
    for r in records:
        if len(r["text"])<200: continue
        # exact-hash prefilter to skip identical texts fast
        exact_hash = hashlib.sha1(r["text"].encode("utf-8")).hexdigest()
        if exact_hash in seen_exact_hashes:
            dropped.append(r["id"]); continue
        seen_exact_hashes.add(exact_hash)

        # sample the first 10k chars to speed up shingling/minhash
        sample_text = r["text"][:10000]
        mh = mhash(sample_text)
        near = lsh.query(mh)
        if near:
            dropped.append(r["id"]); continue
        # Ensure unique key by adding source prefix if needed
        key = f"{r['source']}_{r['id']}"
        if key in seen_ids:
            key = f"{r['source']}_{r['id']}_{len(seen_ids)}"
        seen_ids.add(key)
        lsh.insert(key, mh)
        kept.append(r)
    out_all = Path(args.out)/"corpus_all.jsonl"
    Path(args.out).mkdir(parents=True, exist_ok=True)
    with open(out_all, "w", encoding="utf-8") as f:
        for r in kept: f.write(orjson.dumps(r).decode()+"\n")
    print(f"Kept {len(kept)} | Dropped {len(dropped)} | Wrote {out_all}")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--in", dest="in_", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--prefer", default="permissive-first")
    main(p.parse_args())
