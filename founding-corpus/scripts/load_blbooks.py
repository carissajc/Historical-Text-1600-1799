#!/usr/bin/env python3
"""
Load British Library Books dataset and integrate into main corpus pipeline.
This script runs the blbooks ingestion and converts output to main pipeline format.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
import pandas as pd
import orjson

def run_blbooks_ingestion(args):
    """Run the blbooks ingestion pipeline"""
    print(f"Starting BL books ingestion for years {args.year_min}-{args.year_max}...")
    
    # Create output directory for blbooks
    bl_out = Path(args.out) / "blbooks_temp"
    bl_out.mkdir(parents=True, exist_ok=True)
    
    # Run blbooks ingestion
    cmd = [
        sys.executable, "-m", "blbooks.bl_ingest", "run",
        "--mode", "auto",
        "--config_name", "1700_1799",
        "--year_min", str(args.year_min),
        "--year_max", str(args.year_max),
        "--languages", "English",
        "--skip_empty_pages", "true",
        "--out", str(bl_out),
        "--write_corpus", "true"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("BL books ingestion completed successfully")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"BL books ingestion failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    
    return True

def convert_blbooks_to_main_format(bl_out, main_out):
    """Convert blbooks output to main pipeline JSONL format"""
    print("Converting BL books output to main pipeline format...")
    
    # Read the corpus text file
    corpus_path = bl_out / "corpus.txt"
    if not corpus_path.exists():
        print(f"Corpus file not found: {corpus_path}")
        return False
    
    # Read manifest for metadata
    manifest_path = bl_out / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    
    # Convert to main pipeline format
    output_records = []
    with open(corpus_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            text = line.strip()
            if len(text) < 100:  # Skip very short texts
                continue
                
            record = {
                "id": f"blbooks_{i:06d}",
                "source": "blbooks",
                "text": text,
                "license_tag": "PublicDomain",  # BL books are public domain
                "year": None,  # Will be filled from manifest if available
                "title": None,
                "author": None
            }
            
            # Try to extract year from manifest if available
            if manifest and "date_range" in manifest:
                record["year"] = manifest["date_range"][0]  # Use min year as approximation
            
            output_records.append(record)
    
    # Write to main pipeline format
    output_path = main_out / "blbooks.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in output_records:
            f.write(orjson.dumps(record).decode() + '\n')
    
    print(f"Converted {len(output_records)} BL books records to {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Load BL books and integrate into main corpus")
    parser.add_argument("--out", required=True, help="Output directory for main pipeline")
    parser.add_argument("--year-min", type=int, default=1730, help="Minimum year")
    parser.add_argument("--year-max", type=int, default=1779, help="Maximum year")
    parser.add_argument("--skip-bl-ingestion", action="store_true", 
                       help="Skip BL ingestion (use existing output)")
    parser.add_argument("--bl-output", help="Use existing BL output directory")
    
    args = parser.parse_args()
    
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if args.skip_bl_ingestion and args.bl_output:
        bl_out = Path(args.bl_output)
    else:
        # Run BL books ingestion
        if not run_blbooks_ingestion(args):
            return 1
        
        bl_out = out_dir / "blbooks_temp"
    
    # Convert to main pipeline format
    if not convert_blbooks_to_main_format(bl_out, out_dir):
        return 1
    
    print("BL books integration completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 