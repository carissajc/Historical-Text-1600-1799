# founding-corpus

A reproducible pipeline to assemble a 1777–1797 English corpus from:
- Founders Online (CC-BY-NC)
- Evans-TCP (Public Domain)
- ECCO-TCP (Public Domain)
- American Stories (CC-BY-4.0)
- A Century of Lawmaking (Public Domain)
- Old Bailey (CC-BY-NC)

Outputs normalized JSONL, deduplicated corpora, shards, and a 30k cased WordPiece tokenizer.

Usage

- Default includes NC content:

```bash
make all
```

- Permissive (PD + CC-BY-4.0 only):

```bash
make permissive
```

See `configs/years.yml` and `configs/licenses.yml`. The default allows NC content; gate NC sources with the `--allow-nc` flag or `make permissive`.

## Public-domain verification helper
We provide a small verifier to check the public-domain status of:
- Blackstone’s Commentaries (1765–1769 and 19th‑c editions)
- Johnson’s Dictionary (1755)
- Statutes of the Realm (1810–1825 volumes)

It queries HathiTrust (brief JSON), Internet Archive (advancedsearch), and Google Books APIs to collect rights hints (e.g., Hathi rightsCode pd/pdus, IA license/rights fields, Google Books publicDomain/viewability). It then writes a plain‑English summary and a machine‑readable JSON with recommended sources (favoring scans/facsimiles and older scholarly editions; avoid modern annotated editions).

Run:
```bash
python pd_check.py --out out
# Produces out/PD_REPORT.txt and out/PD_REPORT.json
```