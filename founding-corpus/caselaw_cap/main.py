import argparse
from pathlib import Path
from typing import Dict, Any, List
from datasets import load_dataset
from tqdm import tqdm
import xxhash
import pandas as pd
from .date_extract import header_region, parse_first_date
from .io_utils import ensure_dir, write_parquet_shard, write_jsonl_gz
from .spm_train import train_sentencepiece, spm_tokenize_stats


def stream_ingest(out_dir: Path, batch_size: int = 2000, shard_rows: int = 10000, max_docs: int | None = None) -> None:
    raw_dir = out_dir / "raw_pre1800"
    ensure_dir(raw_dir)
    ds = load_dataset("common-pile/caselaw_access_project", split="train", streaming=True)

    buffer: List[Dict[str, Any]] = []
    shard_idx = 1
    seen = 0

    def flush():
        nonlocal shard_idx, buffer
        if not buffer:
            return
        pq_path = raw_dir / f"part-{shard_idx:05d}.parquet"
        gz_path = raw_dir / f"part-{shard_idx:05d}.jsonl.gz"
        write_parquet_shard(buffer, pq_path)
        write_jsonl_gz(buffer, gz_path)
        buffer = []
        shard_idx += 1

    batch: List[Dict[str, Any]] = []
    for i, row in enumerate(tqdm(ds, desc="streaming")):
        if max_docs and i >= max_docs:
            break
        text = row.get('text') or ''
        if not text:
            continue
        hdr = header_region(text)
        dm = parse_first_date(hdr)
        if not dm or dm.year is None:
            continue
        if dm.year >= 1800:
            continue
        # id
        h = xxhash.xxh64(text).hexdigest()
        rec = {
            'id': h,
            'date_str': dm.date_str,
            'date_year': dm.year,
            'date_offset': dm.offset,
            'text': text,
        }
        batch.append(rec)

        if len(batch) >= batch_size:
            buffer.extend(batch)
            batch = []
        if len(buffer) >= shard_rows:
            flush()

    # flush any leftovers
    buffer.extend(batch)
    flush()


def cmd_train_spm(in_dir: Path, out_dir: Path, vocab_size: int) -> None:
    corpus = sorted(in_dir.glob("part-*.jsonl.gz"))
    if not corpus:
        # fallback to parquet: convert to JSONL quickly
        corpus = sorted(in_dir.glob("part-*.parquet"))
    model_path = train_sentencepiece(corpus, out_dir, vocab_size=vocab_size)
    stats = spm_tokenize_stats(model_path, corpus)
    (out_dir / "stats.json").write_text(__import__('json').dumps(stats, indent=2))
    print("SPM stats:", stats)


def cmd_stats(in_dir: Path, spm_model: Path) -> None:
    corpus = sorted(in_dir.glob("part-*.jsonl.gz"))
    if not corpus:
        corpus = sorted(in_dir.glob("part-*.parquet"))
    stats = spm_tokenize_stats(spm_model, corpus)
    print("SPM stats:", stats)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)

    p_ing = sub.add_parser('ingest')
    p_ing.add_argument('--out-dir', required=True)
    p_ing.add_argument('--batch-size', type=int, default=2000)
    p_ing.add_argument('--shard-rows', type=int, default=10000)
    p_ing.add_argument('--max-docs', type=int)

    p_spm = sub.add_parser('train-spm')
    p_spm.add_argument('--in-dir', required=True)
    p_spm.add_argument('--out-dir', required=True)
    p_spm.add_argument('--vocab-size', type=int, default=30000)

    p_stats = sub.add_parser('stats')
    p_stats.add_argument('--in-dir', required=True)
    p_stats.add_argument('--spm-model', required=True)

    p_all = sub.add_parser('all')
    p_all.add_argument('--out-dir', required=True)
    p_all.add_argument('--vocab-size', type=int, default=30000)
    p_all.add_argument('--max-docs', type=int)

    args = p.parse_args()
    if args.cmd == 'ingest':
        stream_ingest(Path(args.out_dir), args.batch_size, args.shard_rows, args.max_docs)
    elif args.cmd == 'train-spm':
        cmd_train_spm(Path(args.in_dir), Path(args.out_dir), args.vocab_size)
    elif args.cmd == 'stats':
        cmd_stats(Path(args.in_dir), Path(args.spm_model))
    elif args.cmd == 'all':
        out = Path(args.out_dir)
        stream_ingest(out, max_docs=args.max_docs)
        cmd_train_spm(out / 'raw_pre1800', out / 'spm', args.vocab_size)


if __name__ == '__main__':
    main()

