# British Library Books (English, 1730–1779) Ingestion

This mini-project ingests the Hugging Face dataset `TheBritishLibrary/blbooks` and extracts English texts published 1730–1779, assembles page-level OCR into book-level documents, deduplicates, and folds the result into a main corpus (shards + manifest). A plain-English log is appended to `out/LOG.txt`.

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r blbooks/requirements.txt
```

## Two loading modes
- Direct (fast): uses `datasets.load_dataset(..., trust_remote_code=True)` to run the dataset loading script. We enable this because it’s an official BL dataset; we log that we did so.
- Convert (safe): pre-materialize to Parquet via `datasets.commands.convert_to_parquet` and then load from Parquet without running arbitrary code at runtime.

## Examples
Convert to Parquet (optional safe path):
```bash
python -m blbooks.bl_ingest convert --out data/bl_parquet --config_name 1700_1799
```

Run end-to-end (load/filter → assemble → dedup → write → fold):
```bash
python -m blbooks.bl_ingest run \
  --mode auto \
  --config_name 1700_1799 \
  --year_min 1730 --year_max 1779 \
  --languages English \
  --skip_empty_pages true \
  --out out/blbooks_1730_1779_en \
  --main_corpus_dir ../main_corpus \
  --near_dup_thresh 0.8 \
  --write_corpus true
```

## Notes
- License: The dataset card indicates CC Public Domain Mark 1.0. We still prefer facsimiles and avoid modern annotated editions.
- OCR noisiness: We perform light cleanup, preserve original spelling/case, and merge simple hyphenations. Running headers/footers are only lightly filtered.
- Dedup: exact hash (whitespace collapsed) + MinHash LSH (5-grams, Jaccard≥0.8). For collisions we keep the book with the higher mean OCR word count or longer length.
- Outputs: Parquet shards under `out/blbooks_1730_1779_en/books/part-*.parquet`, optional page shards, corpus.txt, manifest.json, dedup_report.json, and `out/LOG.txt` entries understandable to non‑technical readers.