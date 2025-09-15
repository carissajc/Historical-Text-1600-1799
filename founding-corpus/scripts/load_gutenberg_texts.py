import argparse, re
from pathlib import Path
from _util import write_jsonl, clean_text_basic

CANDIDATE_URLS = [
    "https://www.gutenberg.org/files/{id}/{id}-0.txt",           # UTF-8
    "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt",
    "https://www.gutenberg.org/ebooks/{id}.txt.utf-8",
]

def fetch_id(sess, gid):
    for tpl in CANDIDATE_URLS:
        u = tpl.format(id=gid)
        r = sess.get(u, timeout=60)
        if r.status_code == 200 and len(r.text) > 5000:
            return r.text
    return ""

def main(args):
    from _util import session
    s = session()
    ids = [ln.strip() for ln in open(args.ids) if ln.strip() and not ln.startswith("#")]
    out = []
    for gid in ids:
        txt = fetch_id(s, gid)
        if not txt: continue
        # crude header/footer strip
        txt = re.split(r"\*\*\* START OF.*? \*\*\*", txt, flags=re.I|re.S)[-1]
        txt = re.split(r"\*\*\* END OF.*? \*\*\*", txt, flags=re.I|re.S)[0]
        out.append({
            "id": f"gutenberg_{gid}",
            "source":"gutenberg_selected",
            "date":"",  # unknown/varies; fine for tokenizer training
            "license_tag":"PublicDomain",
            "text": clean_text_basic(txt),
            "meta":{"gutenberg_id": gid}
        })
    Path(args.out).mkdir(parents=True, exist_ok=True)
    write_jsonl(Path(args.out)/"gutenberg_selected.jsonl", out)

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ids", required=True)   # text file of Gutenberg IDs (one per line)
    p.add_argument("--out", required=True)
    main(p.parse_args()) 