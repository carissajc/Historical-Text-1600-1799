#!/usr/bin/env python3
"""
Load historical legal decisions from Caselaw Access Project zip files.
This script processes the JSON files within zip archives to extract authentic
colonial and early American legal decisions (pre-1800).
"""

import argparse
import json
import zipfile
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from _util import write_jsonl, clean_text_basic


def parse_args():
    parser = argparse.ArgumentParser(description="Load historical caselaw from CAP zip files")
    parser.add_argument("--in-dir", required=True, help="Directory containing CAP zip files")
    parser.add_argument("--out", required=True, help="Output directory for processed data")
    parser.add_argument("--max-files", type=int, default=None, help="Maximum zip files to process (for testing)")
    return parser.parse_args()


def extract_year_from_date(date_str: str) -> Optional[int]:
    """Extract year from decision_date string (e.g., '1729-10' -> 1729)."""
    if not date_str:
        return None
    
    # Handle various date formats
    # "1729-10" -> 1729
    # "1729" -> 1729
    # "1729-10-15" -> 1729
    
    year_match = re.search(r'(\d{4})', date_str)
    if year_match:
        year = int(year_match.group(1))
        # Filter to reasonable historical range
        if 1600 <= year <= 1799:
            return year
    
    return None


def process_caselaw_json(json_data: Dict[str, Any], zip_name: str, json_file: str) -> Optional[Dict[str, Any]]:
    """Process a single caselaw JSON file and convert to main pipeline format."""
    try:
        # Extract key fields
        decision_date = json_data.get('decision_date', '')
        case_name = json_data.get('name', '')
        case_id = json_data.get('id', '')
        
        # Extract year and filter
        year = extract_year_from_date(decision_date)
        if not year:
            return None
        
        # Get the legal opinion text
        opinions = json_data.get('casebody', {}).get('opinions', [])
        if not opinions:
            return None
        
        # Combine all opinions into one text
        opinion_texts = []
        for opinion in opinions:
            if opinion.get('text'):
                opinion_texts.append(opinion['text'])
        
        if not opinion_texts:
            return None
        
        full_text = '\n\n'.join(opinion_texts)
        
        # Get head matter (summary/metadata)
        head_matter = json_data.get('casebody', {}).get('head_matter', '')
        
        # Get citations
        citations = json_data.get('citations', [])
        citation_text = '; '.join([cite.get('cite', '') for cite in citations if cite.get('cite')])
        
        # Get court information
        court_info = json_data.get('court', {})
        court_name = court_info.get('name', '') if court_info else ''
        
        # Get jurisdiction
        jurisdiction = json_data.get('jurisdiction', {})
        state = jurisdiction.get('name_long', '') if jurisdiction else ''
        
        # Create document record
        document = {
            "id": f"cap_{year}_{case_id}_{zip_name}_{json_file}",
            "source": "historical_caselaw_access",
            "date": f"{year}-01-01",  # Use year-01-01 format for consistency
            "license_tag": "PublicDomain",
            "text": clean_text_basic(full_text),
            "meta": {
                "decision_date": decision_date,
                "year": year,
                "case_name": case_name,
                "case_id": case_id,
                "head_matter": clean_text_basic(head_matter) if head_matter else "",
                "citations": citation_text,
                "court": court_name,
                "state": state,
                "zip_file": zip_name,
                "json_file": json_file,
                "word_count": len(full_text.split()),
                "char_count": len(full_text)
            }
        }
        
        return document
        
    except Exception as e:
        print(f"Error processing {json_file}: {e}")
        return None


def process_caselaw_zip(zip_path: Path) -> List[Dict[str, Any]]:
    """Process a single caselaw zip file and extract all JSON documents."""
    documents = []
    zip_name = zip_path.stem
    
    print(f"  Processing {zip_path.name}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # Find all JSON files
            json_files = [f for f in zip_file.namelist() if f.startswith('json/') and f.endswith('.json')]
            
            print(f"    Found {len(json_files)} JSON files")
            
            for json_file in json_files:
                try:
                    # Read and parse JSON
                    with zip_file.open(json_file) as f:
                        json_content = f.read().decode('utf-8')
                        json_data = json.loads(json_content)
                    
                    # Process the JSON data
                    document = process_caselaw_json(json_data, zip_name, json_file)
                    if document:
                        documents.append(document)
                    
                except json.JSONDecodeError as e:
                    print(f"    Error parsing {json_file}: {e}")
                    continue
                except Exception as e:
                    print(f"    Error processing {json_file}: {e}")
                    continue
    
    except Exception as e:
        print(f"    Error opening zip {zip_path.name}: {e}")
    
    print(f"    Extracted {len(documents)} documents from {zip_path.name}")
    return documents


def main():
    args = parse_args()
    
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out)
    
    if not in_dir.exists():
        print(f"Input directory not found: {in_dir}")
        return
    
    print(f"Loading historical caselaw from {in_dir}")
    print(f"Output directory: {out_dir}")
    
    # Find all zip files
    zip_files = list(in_dir.glob("*.zip"))
    zip_files.sort()
    
    if not zip_files:
        print("No zip files found!")
        return
    
    print(f"Found {len(zip_files)} zip files")
    
    # Limit files if testing
    if args.max_files:
        zip_files = zip_files[:args.max_files]
        print(f"Processing first {len(zip_files)} files (testing mode)")
    
    # Process each zip file
    all_documents = []
    year_counts = {}
    
    for zip_file in zip_files:
        documents = process_caselaw_zip(zip_file)
        all_documents.extend(documents)
        
        # Count by year
        for doc in documents:
            year = doc['meta']['year']
            year_counts[year] = year_counts.get(year, 0) + 1
    
    if not all_documents:
        print("No documents extracted!")
        return
    
    # Create output directory
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save all documents
    write_jsonl(out_dir / "historical_caselaw_all.jsonl", all_documents)
    
    # Save by year
    for year in sorted(year_counts.keys()):
        year_docs = [d for d in all_documents if d['meta']['year'] == year]
        if year_docs:
            write_jsonl(out_dir / f"historical_caselaw_{year}.jsonl", year_docs)
    
    print(f"\nTotal documents extracted: {len(all_documents)}")
    print("Documents by year:")
    for year in sorted(year_counts.keys()):
        print(f"  {year}: {year_counts[year]} documents")
    
    print(f"\nHistorical caselaw data saved to {out_dir}")


if __name__ == "__main__":
    main() 