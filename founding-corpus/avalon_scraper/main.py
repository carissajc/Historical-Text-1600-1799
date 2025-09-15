from __future__ import annotations
import argparse
import asyncio
from pathlib import Path
import pandas as pd
from .crawler import AvalonCrawler
from .storage import Storage
from .logging_utils import HumanLogger


def cmd_crawl(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    crawler = AvalonCrawler(out, concurrency=args.concurrency, delay=args.delay)
    try:
        asyncio.run(crawler.crawl(args.seed))
    finally:
        try:
            asyncio.run(crawler.close())
        except RuntimeError:
            pass


def cmd_resume(args):
    out = Path(args.out)
    state = Storage(out).load_state()
    visited = len(state.get("visited", {}))
    HumanLogger(out).write(f"Resume requested. Already visited {visited} URLs. New crawl will continue from seed.")
    # For simplicity, just re-run crawl; visited set will skip completed
    cmd_crawl(argparse.Namespace(seed=args.seed, out=args.out, concurrency=args.concurrency, delay=args.delay))


def cmd_audit(args):
    out = Path(args.out)
    csv_path = out / "index.csv"
    if not csv_path.exists():
        print("No index.csv found.")
        return
    df = pd.read_csv(csv_path)
    total = len(df)
    words = int(df["word_count"].fillna(0).sum())
    print(f"Documents: {total}")
    print(f"Total words: {words:,}")
    print("Sample rows:")
    print(df[["title","url","date_text","word_count","path"]].head(10).to_string(index=False))


def main():
    p = argparse.ArgumentParser(description="Avalon 18th-century crawler")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("crawl")
    pc.add_argument("--seed", required=True)
    pc.add_argument("--out", required=True)
    pc.add_argument("--concurrency", type=int, default=5)
    pc.add_argument("--delay", type=float, default=0.75)
    pc.set_defaults(func=cmd_crawl)

    pr = sub.add_parser("resume")
    pr.add_argument("--seed", required=True)
    pr.add_argument("--out", required=True)
    pr.add_argument("--concurrency", type=int, default=5)
    pr.add_argument("--delay", type=float, default=0.75)
    pr.set_defaults(func=cmd_resume)

    pa = sub.add_parser("audit")
    pa.add_argument("--out", required=True)
    pa.set_defaults(func=cmd_audit)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()