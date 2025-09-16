

A comprehensive dataset and pipeline for building historical text corpora and training domain-specific  models for historical documents from the 1777-1797 period.

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
git clone https://github.com/yourusername/historicalbert.git
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
- **American Stories** (CC-BY-4.0): Historical narratives
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
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/historicalbert}
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
  - Zips: `founding-corpus/data_raw/caselaw_access_project/`
    - `1 (1).zip`
    - `1 (10).zip`
    - `1 (11).zip`
    - `1 (12).zip`
    - `1 (13).zip`
    - `1 (14).zip`
    - `1 (15).zip`
    - `1 (16).zip`
    - `1 (17).zip`
    - `1 (18).zip`
    - `1 (19).zip`
    - `1 (2).zip`
    - `1 (20).zip`
    - `1 (21).zip`
    - `1 (22).zip`
    - `1 (23).zip`
    - `1 (24).zip`
    - `1 (25).zip`
    - `1 (26).zip`
    - `1 (27).zip`
    - `1 (28).zip`
    - `1 (29).zip`
    - `1 (3).zip`
    - `1 (30).zip`
    - `1 (31).zip`
    - `1 (32).zip`
    - `1 (33).zip`
    - `1 (35).zip`
    - `1 (4).zip`
    - `1 (5).zip`
    - `1 (6).zip`
    - `1 (8).zip`
    - `1 (9).zip`
    - `1-2.zip`
    - `1.zip`
    - `2 (1).zip`
    - `2 (2).zip`
    - `2 (3).zip`
    - `2 (4).zip`
    - `2 (5).zip`
    - `2 (6).zip`
    - `2 (7).zip`
    - `2 (8).zip`
    - `2 (9).zip`
    - `2.zip`
    - `3 (1).zip`
    - `3 (2).zip`
    - `3.zip`
    - `4.zip`

- ECCO-TCP
  - XML files:
    - `founding-corpus/data_raw/ecco_tcp/K000039.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000122.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000152.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000180.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000266.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000268.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000335.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000343.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000379.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000406.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000415.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000454.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000532.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000637.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000663.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000685.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000691.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000780.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000791.000.p4.xml`
    - `founding-corpus/data_raw/ecco_tcp/K000841.000.p4.xml`
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

- Faro de Vigo (yearly JSONL)
  - `founding-corpus/data_raw/faro/faro_1770.jsonl` — 185 records
  - `founding-corpus/data_raw/faro/faro_1771.jsonl` — 709 records
  - `founding-corpus/data_raw/faro/faro_1772.jsonl` — 1,710 records
  - `founding-corpus/data_raw/faro/faro_1773.jsonl` — 1,401 records
  - `founding-corpus/data_raw/faro/faro_1774.jsonl` — 1,644 records
  - `founding-corpus/data_raw/faro/faro_1777.jsonl` — 877 records
  - `founding-corpus/data_raw/faro/faro_1778.jsonl` — 689 records
  - `founding-corpus/data_raw/faro/faro_1779.jsonl` — 410 records
  - `founding-corpus/data_raw/faro/faro_1791.jsonl` — 115 records
  - `founding-corpus/data_raw/faro/faro_1792.jsonl` — 136 records
  - `founding-corpus/data_raw/faro/faro_1793.jsonl` — 52 records
  - `founding-corpus/data_raw/faro/faro_all.jsonl` — 7,928 records

- Founders Online
  - `founding-corpus/data_raw/founders_online/founders_online_1777_1797.jsonl` — 11 records
  - `founding-corpus/data_raw/founders_online/founders_online_all.jsonl` — 16 records

- Gutenberg
  - `founding-corpus/data_raw/gutenberg/gutenberg_selected.jsonl` — 3 records

- Historical Caselaw (yearly JSONL)
  - Per-year files from 1671 through 1799 (selected years). Exact records per file are listed under Cleaned stage below; raw counts closely match but may include slight differences due to normalization. A complete raw file list exists at `founding-corpus/data_raw/historical_caselaw/` and includes all years shown in the cleaned set.
  - Aggregate:
    - `founding-corpus/data_raw/historical_caselaw/historical_caselaw_all.jsonl` — 6,139 records

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

- Faro de Vigo (yearly JSONL + tarballs)
  - JSONL per year: `founding-corpus/data_clean/faro_*.jsonl` — counts per file:
    - 1770: 185; 1771: 709; 1772: 1,710; 1773: 1,401; 1774: 1,642; 1777: 874; 1778: 689; 1779: 410; 1791: 115; 1792: 136; 1793: 52
  - Aggregated: `founding-corpus/data_clean/faro_all.jsonl` — 7,923 records
  - Tarballs present for several years: `faro_1770.tar.gz`, `faro_1771.tar.gz`, `faro_1772.tar.gz`, `faro_1773.tar.gz`, `faro_1774.tar.gz`, `faro_1777.tar.gz`, `faro_1778.tar.gz`, `faro_1779.tar.gz`, `faro_1791.tar.gz`, `faro_1792.tar.gz`, `faro_1793.tar.gz`

- Founders Online
  - `founding-corpus/data_clean/founders_online.jsonl` — 11 records
  - `founding-corpus/data_clean/founders_online_all.jsonl` — 16 records

- Gutenberg
  - `founding-corpus/data_clean/gutenberg_selected.jsonl` — 3 records

- Historical Caselaw (per-year JSONL; record counts shown)
  - 1671: 33; 1672: 48; 1673: 13; 1674: 9; 1675: 123; 1676: 91; 1677: 144; 1678: 158; 1679: 117; 1680: 49;
  - 1700: 2; 1701: 1; 1702: 1; 1704: 1;
  - 1713: 2; 1714: 4; 1715: 2; 1716: 4; 1717: 7; 1718: 4; 1719: 5;
  - 1720: 1; 1721: 6; 1722: 46; 1723: 16; 1724: 29; 1725: 4; 1726: 25; 1727: 18; 1728: 12; 1729: 22;
  - 1730: 12; 1731: 33; 1732: 17; 1733: 43; 1734: 10; 1735: 25; 1736: 32; 1737: 16; 1738: 9; 1739: 18; 1740: 12; 1741: 12; 1742: 1; 1743: 13;
  - 1745: 14; 1746: 5; 1747: 22; 1748: 7; 1749: 10; 1750: 20; 1751: 10; 1752: 19; 1753: 3; 1754: 7; 1755: 3; 1756: 3; 1757: 12; 1758: 11; 1759: 14; 1760: 12; 1761: 6; 1762: 39; 1763: 48; 1764: 68; 1765: 36; 1766: 27; 1767: 10; 1768: 17; 1769: 8;
  - 1770: 14; 1771: 39; 1772: 59; 1773: 64; 1774: 22; 1775: 10; 1776: 9; 1777: 3; 1778: 14; 1779: 4; 1780: 9; 1781: 17; 1782: 22; 1783: 24; 1784: 69; 1785: 109; 1786: 161; 1787: 141; 1788: 221; 1789: 161; 1790: 235; 1791: 325; 1792: 365; 1793: 571; 1794: 244; 1795: 271; 1796: 211; 1797: 191; 1798: 154; 1799: 421
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
