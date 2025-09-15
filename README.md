# HistoricalBERT

A comprehensive pipeline for building historical text corpora and training domain-specific BERT models for historical documents from the 1777-1797 period.

## Overview

This repository contains tools and pipelines for:

- **Corpus Assembly**: Collecting and processing historical texts from multiple sources
- **Data Processing**: Cleaning, normalizing, and deduplicating historical documents
- **Tokenizer Training**: Creating domain-specific WordPiece tokenizers
- **Model Training**: Training BERT models on historical corpora

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
  title={HistoricalBERT: A Pipeline for Historical Text Corpora and Domain-Specific BERT Models},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/historicalbert}
}
```

## Contact

For questions or issues, please open a GitHub issue or contact [your-email@domain.com].
