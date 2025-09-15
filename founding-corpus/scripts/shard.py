import argparse, os, math, orjson
from pathlib import Path

def main(args):
    inp = Path(args.inp); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    target = int(float(args.target_mb)*1024*1024)
    with open(inp, "r", encoding="utf-8") as f:
        buf=[]; sz=0; idx=0
        def flush():
            nonlocal buf, sz, idx
            p = out/f"shard_{idx:05d}.txt"
            with open(p,"w",encoding="utf-8") as w:
                for r in buf: w.write(r+"\n")
            buf=[]; sz=0; idx+=1
        for line in f:
            rec = orjson.loads(line); text = rec["text"].replace("\n"," ").strip()
            if not text: continue
            s = text.encode("utf-8"); L=len(s)
            if sz+L>target and buf: flush()
            buf.append(text); sz+=L
        if buf: flush()
    print("Shards at", out)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", required=True); p.add_argument("--target-mb", default="75")
    main(p.parse_args())
