import argparse, orjson, glob, collections, os
from tokenizers import Tokenizer

def count_lines(path):
    c=0
    with open(path, "r", encoding="utf-8") as f:
        for _ in f: c+=1
    return c

def main(args):
    # doc counts by source/license
    src=collections.Counter(); lic=collections.Counter()
    for fp in glob.glob(f"{args.clean}/*.jsonl"):
        for line in open(fp, encoding="utf-8"):
            r=orjson.loads(line); src[r["source"]]+=1; lic[r["license_tag"]]+=1
    print("CLEAN docs by source:", src)
    print("CLEAN docs by license:", lic)
    if os.path.exists(f"{args.dedup}/corpus_all.jsonl"):
        print("DEDUP lines:", count_lines(f"{args.dedup}/corpus_all.jsonl"))
    # tokenizer vocab size
    if os.path.exists(f"{args.tok}/tokenizer.json"):
        tok=Tokenizer.from_file(f"{args.tok}/tokenizer.json")
        print("Tokenizer vocab:", len(tok.get_vocab()))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--clean", required=True)
    p.add_argument("--dedup", required=True)
    p.add_argument("--tok", required=True)
    main(p.parse_args())
