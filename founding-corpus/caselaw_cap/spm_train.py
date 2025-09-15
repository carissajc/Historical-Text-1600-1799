from __future__ import annotations
from typing import Iterable
from pathlib import Path
import sentencepiece as spm
import tempfile, os, gzip


def train_sentencepiece(corpus_files: Iterable[Path], out_dir: Path, vocab_size: int = 30000, model_prefix: str = "spm") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Create a temporary concatenated training file
    with tempfile.TemporaryDirectory() as td:
        train_path = Path(td) / "train.txt"
        with open(train_path, 'w', encoding='utf-8') as out_f:
            for p in corpus_files:
                opener = gzip.open if p.suffix == '.gz' else open
                with opener(p, 'rt', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        # expects JSONL with field text or raw text lines
                        out_f.write(line if not line.startswith('{') else _extract_text(line))
        spm.SentencePieceTrainer.Train(
            input=str(train_path),
            model_prefix=str(out_dir / model_prefix),
            vocab_size=vocab_size,
            character_coverage=1.0,
            model_type='unigram'
        )
    return out_dir / f"{model_prefix}.model"


def _extract_text(jsonl_line: str) -> str:
    # very small, fast JSONL text extractor without full parse
    try:
        import orjson
        obj = orjson.loads(jsonl_line)
        return (obj.get('text') or '') + '\n'
    except Exception:
        return '\n'


def spm_tokenize_stats(model_path: Path, corpus_files: Iterable[Path]) -> dict:
    sp = spm.SentencePieceProcessor()
    sp.load(str(model_path))
    total_chars = 0
    total_tokens = 0
    num_docs = 0

    for p in corpus_files:
        opener = gzip.open if p.suffix == '.gz' else open
        with opener(p, 'rt', encoding='utf-8', errors='ignore') as f:
            for line in f:
                text = line.strip()
                if text.startswith('{'):
                    text = _extract_text(line)
                text = text.strip()
                if not text:
                    continue
                tokens = sp.encode(text, out_type=str)
                total_chars += len(text)
                total_tokens += len(tokens)
                num_docs += 1

    return {
        'num_docs': num_docs,
        'total_chars': total_chars,
        'total_tokens': total_tokens,
        'avg_chars_per_doc': (total_chars / num_docs) if num_docs else 0,
        'avg_tokens_per_doc': (total_tokens / num_docs) if num_docs else 0,
        'avg_chars_per_token': (total_chars / total_tokens) if total_tokens else 0,
    }

