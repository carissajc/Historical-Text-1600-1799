Caselaw Access Project (CAP) streaming pipeline

CLI to stream `common-pile/caselaw_access_project` from Hugging Face, extract the first decision date near the start, filter to year < 1800, write Parquet/JSONL shards, train a SentencePiece tokenizer, and report tokenization stats.

Quickstart

1) Install deps

```
pip install -r caselaw_cap/requirements.txt
```

2) Ingest (stream) and filter to pre-1800

```
python caselaw_cap/main.py ingest \
  --out-dir caselaw_cap/out \
  --batch-size 2000 \
  --shard-rows 10000 \
  --max-docs 20000   # optional cap for testing
```

3) Train SentencePiece tokenizer

```
python caselaw_cap/main.py train-spm \
  --in-dir caselaw_cap/out/raw_pre1800 \
  --out-dir caselaw_cap/out/spm \
  --vocab-size 30000
```

4) Tokenization stats

```
python caselaw_cap/main.py stats \
  --in-dir caselaw_cap/out/raw_pre1800 \
  --spm-model caselaw_cap/out/spm/spm.model
```

One-shot

```
python caselaw_cap/main.py all --out-dir caselaw_cap/out --vocab-size 30000 --max-docs 20000
```

