#!/usr/bin/env python3
"""
Convert existing CAP data from the caselaw_cap module to main pipeline format.
This script processes the existing part-00001.jsonl.gz file and converts it.
"""

import argparse
import gzip
import json
import sys
from pathlib import Path
from typing import Dict, Any
from _util import write_jsonl, clean_text_basic

# Import CAP date extraction utilities with corrected logic
sys.path.append(str(Path(__file__).parent.parent / "caselaw_cap"))
from date_extract import header_region, parse_first_date


def parse_args():
    parser = argparse.ArgumentParser(description="Convert existing CAP data to main pipeline format")
    parser.add_argument("--in-file", required=True, help="Input CAP JSONL.gz file")
    parser.add_argument("--out", required=True, help="Output directory for converted data")
    return parser.parse_args()


def convert_cap_document(cap_doc: Dict[str, Any]) -> Dict[str, Any] | None:
    """Convert a CAP document to main pipeline format."""
    try:
        # Extract fields from CAP format
        text = cap_doc.get('text', '')
        if not text or len(text) < 100:
            return None
        
        # Re-extract date using corrected logic to filter out false positives
        header = header_region(text)
        date_match = parse_first_date(header)
        
        # Only accept documents with valid dates that have month, day, and year
        if not date_match or date_match.year is None:
            return None
        
        # Additional validation: ensure year is in reasonable range for historical documents
        if date_match.year < 1500 or date_match.year > 1799:
            return None
        
        date_str = date_match.date_str
        date_year = date_match.year
        date_offset = date_match.offset
        
        # Create document ID (use existing hash if available, otherwise generate new one)
        doc_id = cap_doc.get('id', f"cap_{date_year}_{date_offset}")
        
        # Convert to main pipeline format
        document = {
            "id": doc_id,
            "source": "caselaw_access_project",
            "date": date_str,
            "license_tag": "PublicDomain",
            "text": clean_text_basic(text),
            "meta": {
                "date_year": date_year,
                "date_offset": date_offset,
                "dataset": "common-pile/caselaw_access_project",
                "converted_from": "existing_cap_module",
                "date_extraction_method": "corrected_logic"
            }
        }
        
        return document
        
    except Exception as e:
        print(f"Error converting document: {e}")
        return None


def main():
    args = parse_args()
    
    in_file = Path(args.in_file)
    out_dir = Path(args.out)
    
    if not in_file.exists():
        print(f"Input file not found: {in_file}")
        return
    
    print(f"Converting existing CAP data from {in_file}")
    print(f"Output directory: {out_dir}")
    print("Using corrected date extraction logic (month + day + year only)")
    
    # Create output directory
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Read and convert documents
    documents = []
    year_counts = {}
    skipped_count = 0
    
    try:
        with gzip.open(in_file, 'rt', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    cap_doc = json.loads(line.strip())
                    converted_doc = convert_cap_document(cap_doc)
                    
                    if converted_doc:
                        documents.append(converted_doc)
                        year = converted_doc['meta']['date_year']
                        year_counts[year] = year_counts.get(year, 0) + 1
                    else:
                        skipped_count += 1
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing line {line_num}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    if not documents:
        print("No documents converted!")
        return
    
    # Save converted documents
    write_jsonl(out_dir / "caselaw_cap_converted.jsonl", documents)
    
    # Save by year
    for year in sorted(year_counts.keys()):
        year_docs = [d for d in documents if d['meta']['date_year'] == year]
        if year_docs:
            write_jsonl(out_dir / f"caselaw_cap_{year}.jsonl", year_docs)
    
    print(f"\nTotal documents converted: {len(documents)}")
    print(f"Documents skipped (invalid dates): {skipped_count}")
    print("Documents by year:")
    for year in sorted(year_counts.keys()):
        print(f"  {year}: {year_counts[year]} documents")
    
    print(f"\nConverted CAP data saved to {out_dir}")


if __name__ == "__main__":
    main() 