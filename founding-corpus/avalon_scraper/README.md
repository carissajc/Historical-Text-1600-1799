# Avalon 18th-Century Primary Texts Scraper

This tool crawls the Avalon Project (Yale Law) 18th‑century menu, follows nested index pages, and saves clean primary texts with metadata.

## Features
- Respects robots.txt and crawls politely (custom UA, delays, retries with backoff)
- Recursively follows same‑site links until reaching document pages
- Extracts clean text via trafilatura, with BS4 fallback
- Captures metadata (url, title, collection, date_text, html_lang, retrieved_at, parent_url)
- Writes one Markdown document per text with YAML front‑matter
- Maintains a master CSV and Parquet index
- Human‑readable crawl log in `out/LOG.txt`
- Resume support via `out/state.json`

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r avalon_scraper/requirements.txt
```

## Run
```bash
python -m avalon_scraper.main crawl \
  --seed https://avalon.law.yale.edu/subject_menus/18th.asp \
  --out out \
  --concurrency 5 \
  --delay 0.75

python -m avalon_scraper.main resume \
  --seed https://avalon.law.yale.edu/subject_menus/18th.asp \
  --out out

python -m avalon_scraper.main audit --out out
```

## Outputs
- `out/LOG.txt` – plain‑English activity log
- `out/docs/*.md` – one Markdown per document with YAML front‑matter
- `out/index.csv` and `out/index.parquet` – master index
- `out/state.json` – resume state (visited URLs, outputs)

## Notes
- PDFs: If an HTML page links to a canonical PDF only, the scraper downloads and extracts text (quality varies). The log records this explicitly.
- Duplicates: Obvious duplicates are skipped by hashing the main text.