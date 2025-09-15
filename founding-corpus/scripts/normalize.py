import argparse, json, glob, orjson
from pathlib import Path
from _util import clean_text_basic

def main(args):
    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)
    for src in Path(args.in_dir).glob("*/*.jsonl"):
        cleaned=[]
        for line in open(src, encoding="utf-8"):
            r = orjson.loads(line)
            r["text"] = clean_text_basic(r["text"])
            if len(r["text"]) >= 100: cleaned.append(r)
        out = outdir/(src.stem.replace("_1777_1797","") + ".jsonl")
        with open(out, "w", encoding="utf-8") as f:
            for r in cleaned: f.write(orjson.dumps(r).decode()+"\n")
    print("Normalized ->", outdir)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--in-dir", required=True); p.add_argument("--out", required=True)
    main(p.parse_args())
