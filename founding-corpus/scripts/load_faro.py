#!/usr/bin/env python3
"""
Load FARO (Founding American Republic Online) dataset from .tar.gz files.
These files contain historical articles organized by year.
"""

import argparse
import json
import tarfile
import os
from pathlib import Path
from typing import Dict, List, Any
import re


def parse_args():
    parser = argparse.ArgumentParser(description="Load FARO dataset from .tar.gz files")
    parser.add_argument("--in-dir", type=str, required=True, help="Input directory containing faro_*.tar.gz files")
    parser.add_argument("--out", type=str, required=True, help="Output directory for processed data")
    return parser.parse_args()


def extract_year_from_filename(filename: str) -> int:
    """Extract year from filename like 'faro_1777.tar.gz'"""
    match = re.search(r'faro_(\d{4})\.tar\.gz', filename)
    if match:
        return int(match.group(1))
    return None


def process_faro_file(tar_path: Path) -> List[Dict[str, Any]]:
    """Process a single FARO .tar.gz file and extract articles."""
    articles = []
    year = extract_year_from_filename(tar_path.name)
    
    if year is None:
        print(f"  Could not extract year from filename: {tar_path.name}")
        return articles
    
    print(f"  Processing {tar_path.name} (year {year})...")
    
    try:
        with tarfile.open(tar_path, 'r:gz') as tar:
            # List all files in the archive
            file_list = tar.getnames()
            print(f"    Archive contains {len(file_list)} files")
            
            for member in tar.getmembers():
                if member.isfile() and member.name.endswith('.json'):
                    # Extract and process JSON files
                    try:
                        f = tar.extractfile(member)
                        if f is not None:
                            content = f.read().decode('utf-8')
                            data = json.loads(content)
                            
                            # Process the article data
                            article = process_article_data(data, year, member.name)
                            if article:
                                articles.extend(article) # Extend the list of articles
                                
                    except Exception as e:
                        print(f"      Error processing {member.name}: {e}")
                        continue
                        
    except Exception as e:
        print(f"    Error opening archive {tar_path.name}: {e}")
        return articles
    
    print(f"    Extracted {len(articles)} articles from year {year}")
    return articles


def process_article_data(data: Any, year: int, filename: str) -> Dict[str, Any]:
    """Process individual article data and convert to our format."""
    try:
        # Handle different possible data structures
        if isinstance(data, dict):
            # Check if this is a FARO-style JSON with bboxes
            if 'bboxes' in data and isinstance(data['bboxes'], list):
                articles = []
                
                # Extract newspaper metadata
                newspaper_info = data.get('lccn', {})
                newspaper_title = newspaper_info.get('title', 'Unknown Newspaper')
                state = newspaper_info.get('state', 'Unknown State')
                date = data.get('edition', {}).get('date', f"{year}-01-01")
                
                # Process each bbox that contains an article
                for bbox in data['bboxes']:
                    if bbox.get('class') == 'article' and bbox.get('raw_text'):
                        text = bbox['raw_text'].strip()
                        
                        # Only keep articles with substantial text
                        if len(text) > 100:
                            article_id = f"faro_{year}_{bbox.get('id', 'unknown')}_{filename}"
                            
                            article = {
                                "id": article_id,
                                "source": "faro",
                                "date": date,
                                "license_tag": "CC0",  # Public domain historical documents
                                "text": text,
                                "meta": {
                                    'newspaper': newspaper_title,
                                    'state': state,
                                    'headline': f"Article {bbox.get('id', 'unknown')}",
                                    'date': date,
                                    'source_file': filename,
                                    'year': year,
                                    'legibility': bbox.get('legibility', 'Unknown'),
                                    'bbox_id': bbox.get('id'),
                                    'reading_order': bbox.get('reading_order_id')
                                }
                            }
                            articles.append(article)
                
                return articles
            
            # Handle other dict formats
            else:
                # Try to extract article information
                article_id = data.get('id') or data.get('article_id') or f"faro_{year}_{filename}"
                
                # Extract text content
                text = data.get('text') or data.get('article') or data.get('content') or data.get('ocr_text', '')
                
                # Extract metadata
                meta = {
                    'newspaper': data.get('newspaper') or data.get('title') or data.get('publication', ''),
                    'headline': data.get('headline') or data.get('title', ''),
                    'date': data.get('date') or f"{year}-01-01",
                    'source_file': filename,
                    'year': year
                }
                
                # Only keep articles with substantial text
                if text and len(text.strip()) > 50:
                    return {
                        "id": article_id,
                        "source": "faro",
                        "date": f"{year}-01-01",
                        "license_tag": "CC0",  # Public domain historical documents
                        "text": text.strip(),
                        "meta": meta
                    }
        
        elif isinstance(data, list):
            # Handle list of articles
            articles = []
            for item in data:
                article = process_article_data(item, year, filename)
                if article:
                    if isinstance(article, list):
                        articles.extend(article)
                    else:
                        articles.append(article)
            return articles
            
        elif isinstance(data, str):
            # Handle plain text
            if len(data.strip()) > 50:
                return {
                    "id": f"faro_{year}_{filename}",
                    "source": "faro",
                    "date": f"{year}-01-01",
                    "license_tag": "CC0",
                    "text": data.strip(),
                    "meta": {
                        'source_file': filename,
                        'year': year
                    }
                }
                
    except Exception as e:
        print(f"      Error processing article data: {e}")
        return None
    
    return None


def main():
    args = parse_args()
    
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out)
    
    print(f"Loading FARO dataset from {in_dir}")
    print(f"Output directory: {out_dir}")
    
    # Find all FARO .tar.gz files
    faro_files = list(in_dir.glob("faro_*.tar.gz"))
    faro_files.sort()  # Sort by filename (which includes year)
    
    if not faro_files:
        print("No FARO .tar.gz files found!")
        return
    
    print(f"Found {len(faro_files)} FARO files:")
    for f in faro_files:
        year = extract_year_from_filename(f.name)
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name} (year {year}, {size_mb:.1f} MB)")
    
    # Process each file
    all_articles = []
    year_counts = {}
    
    for faro_file in faro_files:
        year = extract_year_from_filename(faro_file.name)
        if year is None:
            continue
            
        articles = process_faro_file(faro_file)
        
        # Handle both single articles and lists of articles
        if isinstance(articles, list):
            all_articles.extend(articles)
            year_counts[year] = len(articles)
        else:
            if articles:
                all_articles.append(articles)
                year_counts[year] = 1
    
    # Save the processed data
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save all articles
    with open(out_dir / "faro_all.jsonl", "w") as f:
        for article in all_articles:
            f.write(json.dumps(article) + "\n")
    
    # Save by year
    for year in sorted(year_counts.keys()):
        year_articles = [a for a in all_articles if a.get('meta', {}).get('year') == year]
        if year_articles:
            with open(out_dir / f"faro_{year}.jsonl", "w") as f:
                for article in year_articles:
                    f.write(json.dumps(article) + "\n")
    
    print(f"\nTotal articles processed: {len(all_articles)}")
    print("Articles by year:")
    for year in sorted(year_counts.keys()):
        print(f"  {year}: {year_counts[year]} articles")
    
    print(f"\nFARO data saved to {out_dir}")


if __name__ == "__main__":
    main() 