A comprehensive dataset and pipeline for building historical text corpora and training domain-specific models for historical documents from the 1777-1797 period.

## Overview

This repository contains tools and pipelines for:

- **Corpus Assembly**: Collecting and processing historical texts from multiple sources from the 1777-1797 period
- **Data Processing**: Cleaning, normalizing, and deduplicating historical documents
- **Tokenizer Training**: Creating domain-specific WordPiece tokenizers

## Repository Structure

```
historicalbert/
├── founding-corpus/          # Main corpus processing pipeline
│   ├── scripts/             # Processing scripts
│   ├── configs/             # Configuration files
│   ├── data_raw/            # Raw data sources (excluded from git)
│   ├── data_clean/          # Cleaned data (excluded from git)
│   ├── data_dedup/          # Deduplicated data (excluded from git)
│   └── reports/             # Analysis reports and tokenizers
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd historicalbert
```

2. Set up the environment:
```bash
cd founding-corpus
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the pipeline:
```bash
# Full pipeline (includes all data sources)
make all

# Or permissive only (public domain + CC-BY-4.0)
make permissive
```

## Data Sources

The pipeline integrates multiple historical text sources:

- **Founders Online** (CC-BY-NC): Revolutionary era documents
- **Evans-TCP** (Public Domain): Early American imprints
- **ECCO-TCP** (Public Domain): Eighteenth Century Collections Online
- **American Stories (FARO)** (CC-BY-4.0): Historical narratives from Melissa Dell et al.'s American Stories project (the code refers to this data as FARO)
- **A Century of Lawmaking** (Public Domain): Congressional documents
- **Old Bailey** (CC-BY-NC): Court records
- **British Library Books** (Public Domain): Historical texts
- **Gutenberg** (Public Domain): Classic literature

## Pipeline Stages

1. **Download**: Collect data from various sources
2. **Normalize**: Clean and standardize text
3. **Deduplicate**: Remove duplicate content using MinHash LSH
4. **Shard**: Split into training-ready chunks
5. **Train Tokenizer**: Create WordPiece tokenizer
6. **Report**: Generate statistics and analysis

## Source Acquisition Criteria

- BL Books (British Library Books)
  - Years: 1730–1779; config: `1700_1799`; language: English; skip empty pages; writes consolidated corpus; converted records drop texts <100 chars.

- American Stories (FARO; Melissa Dell et al.)
  - Inputs: yearly `faro_*.tar.gz`; year from filename; prefer bbox JSON with `class=='article'` and `raw_text`; min length >100 chars (or >50 for alternative JSON forms); metadata captured (newspaper/state/date/headline/source filename/year/etc.); license CC0.

- Founders Online
  - Strategies: per-year searches for 1777–1797 using several query URL variants; plus systematic URL pattern exploration across founders/series/volumes; include documents with text >200 chars; best-effort date parse; default to 1777-01-01 if missing; license CC-BY-NC gated by `--allow-nc`.

- Project Gutenberg
  - IDs from `configs/gutenberg_ids.txt`; tries standard PG text URLs in order; require HTTP 200 and >5,000 chars; strips header/footer; license PublicDomain.

- ECCO-TCP and Evans-TCP (TCP)
  - Inputs: local nested zip TEI XML; years from `configs/years.yml`; year extraction via regex preferring `<SOURCEDESC><DATE>`; exclude years outside range and modern years; extract `<TEXT>` content; require text >=100 chars; license PublicDomain; outputs `{corpus}_tcp_{start}_{end}.jsonl`.

## Configuration

- `configs/years.yml`: Date range configuration
- `configs/licenses.yml`: License filtering options
- `configs/gutenberg_ids.txt`: Specific Gutenberg texts to include

## Output

The pipeline generates:

- **Cleaned JSONL files**: Normalized document collections
- **Deduplicated corpus**: Final document set
- **Training shards**: Text files ready for model training
- **WordPiece tokenizer**: Domain-specific vocabulary
- **Analysis reports**: Statistics and metadata

## Current Status

- **Corpus Size**: ~4.6 GB total (2.1GB raw, 937MB clean, 1.6GB deduplicated)
- **Documents**: 20,067 documents after deduplication
- **Tokenizer**: 8,258 vocabulary size
- **Date Range**: 1777-1797 (target period)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project includes data from multiple sources with different licenses:
- Public Domain content
- CC-BY-4.0 content
- CC-BY-NC content (optional, can be excluded)

See individual source documentation for specific licensing terms.

## Citation

If you use this corpus or pipeline in your research, please cite:

```bibtex
@software{historicalbert,
  title={HistoricalCorpus: A Pipeline for Historical Text Corpora and Domain-Specific BERT Models},
  author={Carissa Chen},
  year={2024}
}
```

## Contact

For questions or issues, please open a GitHub issue or contact chencarissa@gmail.com

## Comprehensive Inventory of Historical Texts in This Workspace

The following is an exact, file-based inventory of historical texts and data artifacts present in this repository. Counts reflect the number of JSON Lines records per file where applicable. Items are grouped by source and by processing stage.

### Raw Sources (`founding-corpus/data_raw/`)

- American Stories
  - `founding-corpus/data_raw/american_stories/american_stories.jsonl` — 3 records
  - `founding-corpus/data_raw/american_stories/american_stories_1777_1797.jsonl` — 3 records
  - `founding-corpus/data_raw/american_stories/american_stories_all.jsonl` — 3 records

- BL Books
  - `founding-corpus/data_raw/blbooks/blbooks.jsonl` — 808 records

- Caselaw Access Project (CAP) raw archives
  - Multiple zip archives in `founding-corpus/data_raw/caselaw_access_project/` (35+ files)

- ECCO-TCP
  - XML files: Multiple TEI XML files (19+ files) in `founding-corpus/data_raw/ecco_tcp/`
  - Archives and indices:
    - `founding-corpus/data_raw/ecco_tcp/ecco_all.zip`
    - `founding-corpus/data_raw/ecco_tcp/ecco_p4_released.zip`
    - `founding-corpus/data_raw/ecco_tcp/ecco_tcp_1600_1799.jsonl` — 2,440 records
    - `founding-corpus/data_raw/ecco_tcp/ecco_tcp_1777_1797.jsonl` — 0 records

- Evans-TCP
  - Archives and indices:
    - `founding-corpus/data_raw/evans_tcp/N0.zip`
    - `founding-corpus/data_raw/evans_tcp/N00001.p4.xml`
    - `founding-corpus/data_raw/evans_tcp/P4_XML_TCP.zip`
    - `founding-corpus/data_raw/evans_tcp/evans_tcp_1600_1799.jsonl` — 4,570 records
    - `founding-corpus/data_raw/evans_tcp/evans_tcp_1777_1797.jsonl` — 0 records

- American Stories (FARO; Melissa Dell et al.)
  - Yearly JSONL files: `founding-corpus/data_raw/faro/faro_*.jsonl` (11 yearly files: 1770-1774, 1777-1779, 1791-1793)
  - Aggregate: `founding-corpus/data_raw/faro/faro_all.jsonl` — 7,928 records

- Founders Online
  - `founding-corpus/data_raw/founders_online/founders_online_1777_1797.jsonl` — 11 records
  - `founding-corpus/data_raw/founders_online/founders_online_all.jsonl` — 16 records

- Gutenberg
  - `founding-corpus/data_raw/gutenberg/gutenberg_selected.jsonl` — 3 records

- Historical Caselaw (yearly JSONL)
  - Per-year files from 1671 through 1799 in `founding-corpus/data_raw/historical_caselaw/`
  - Aggregate: `founding-corpus/data_raw/historical_caselaw/historical_caselaw_all.jsonl` — 6,139 records

- Historical Legal
  - `founding-corpus/data_raw/historical_legal/historical_legal_1777_1797.jsonl` — 4 records

- TCP Public
  - `founding-corpus/data_raw/tcp_public/tcp_public_1777_1797.jsonl` — 2 records

### Cleaned Sources (`founding-corpus/data_clean/`)

- American Stories
  - `founding-corpus/data_clean/american_stories.jsonl` — 3 records
  - `founding-corpus/data_clean/american_stories_all.jsonl` — 3 records

- BL Books
  - `founding-corpus/data_clean/blbooks.jsonl` — 808 records

- ECCO-TCP
  - `founding-corpus/data_clean/ecco_tcp.jsonl` — 0 records
  - `founding-corpus/data_clean/ecco_tcp_1600_1799.jsonl` — 2,440 records

- Evans-TCP
  - `founding-corpus/data_clean/evans_tcp.jsonl` — 0 records
  - `founding-corpus/data_clean/evans_tcp_1600_1799.jsonl` — 4,570 records

- American Stories (FARO; Melissa Dell et al.) (yearly JSONL + tarballs)
  - JSONL per year: `founding-corpus/data_clean/faro_*.jsonl` (11 yearly files: 1770-1774, 1777-1779, 1791-1793)
  - Aggregated: `founding-corpus/data_clean/faro_all.jsonl` — 7,923 records
  - Tarballs: Corresponding `faro_*.tar.gz` files for each year

- Founders Online
  - `founding-corpus/data_clean/founders_online.jsonl` — 11 records
  - `founding-corpus/data_clean/founders_online_all.jsonl` — 16 records

- Gutenberg
  - `founding-corpus/data_clean/gutenberg_selected.jsonl` — 3 records

- Historical Caselaw (per-year JSONL files from 1671-1799)
  - Yearly files: `founding-corpus/data_clean/historical_caselaw_*.jsonl` with varying record counts per year
  - Aggregate:
    - `founding-corpus/data_clean/historical_caselaw_all.jsonl` — 5,841 records

- Historical Legal
  - `founding-corpus/data_clean/historical_legal.jsonl` — 4 records

- TCP Public
  - `founding-corpus/data_clean/tcp_public.jsonl` — 2 records

### Deduplicated Corpus (`founding-corpus/data_dedup/`)

- Combined Corpus
  - `founding-corpus/data_dedup/corpus_all.jsonl` — 20,067 records
  - Shards: `founding-corpus/data_dedup/shards/`
    - `shard_00000.txt`
    - `shard_00001.txt`
    - `shard_00002.txt`
    - `shard_00003.txt`
    - `shard_00004.txt`
    - `shard_00005.txt`
    - `shard_00006.txt`
    - `shard_00007.txt`
    - `shard_00008.txt`
    - `shard_00009.txt`
    - `shard_00010.txt`

Note: Paths and counts above are taken directly from the files present in this workspace to avoid speculation.
