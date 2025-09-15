#!/usr/bin/env python3
"""
Load publicly available historical texts that would typically be in TCP collections.
This provides access to foundational historical documents without requiring bulk downloads.
"""

import argparse
import re
import time
from pathlib import Path
from _util import load_years, in_range, session, write_jsonl, clean_text_basic

# Public sources for historical texts
HISTORICAL_SOURCES = [
    {
        "name": "founding_documents",
        "urls": [
            "https://www.archives.gov/founding-docs/declaration-transcript",
            "https://www.archives.gov/founding-docs/constitution-transcript",
            "https://www.archives.gov/founding-docs/bill-of-rights-transcript"
        ],
        "source_tag": "tcp_founding_docs"
    },
    {
        "name": "federalist_papers",
        "urls": [
            "https://www.congress.gov/resources/display/content/The+Federalist+Papers"
        ],
        "source_tag": "tcp_federalist"
    }
]

def fetch_historical_texts(session, start_year, end_year):
    """Fetch historical texts from public sources."""
    out = []
    
    for source in HISTORICAL_SOURCES:
        print(f"Processing {source['name']}...")
        
        for url in source["urls"]:
            try:
                response = session.get(url, timeout=30)
                if response.status_code == 200:
                    # Extract text content (basic approach)
                    text = response.text
                    
                    # Clean HTML and extract meaningful text
                    # This is a simplified approach - in practice you'd want more sophisticated parsing
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if len(text) > 500:  # Minimum meaningful length
                        # Assign appropriate dates based on document type
                        if "declaration" in url.lower():
                            date = "1776-07-04"
                        elif "constitution" in url.lower():
                            date = "1787-09-17"
                        elif "bill-of-rights" in url.lower():
                            date = "1789-09-25"
                        elif "federalist" in url.lower():
                            date = "1787-10-27"  # First Federalist Paper published
                        else:
                            date = f"{start_year}-01-01"
                        
                        year = int(date[:4])
                        if start_year <= year <= end_year:
                            out.append({
                                "id": f"{source['source_tag']}_{len(out)}",
                                "source": source["source_tag"],
                                "date": date,
                                "license_tag": "PublicDomain",
                                "text": clean_text_basic(text),
                                "meta": {
                                    "url": url,
                                    "source_name": source["name"],
                                    "document_type": "founding_document"
                                }
                            })
                
                time.sleep(1)  # Be respectful to servers
                
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue
    
    return out

def main(args):
    start_date, end_date = load_years(args.years)
    start_year = int(start_date[:4])
    end_year = int(end_date[:4])
    
    print(f"Loading TCP-style historical texts for {start_year}-{end_year}")
    
    s = session()
    out = fetch_historical_texts(s, start_year, end_year)
    
    print(f"Total documents found: {len(out)}")
    
    Path(args.out).mkdir(parents=True, exist_ok=True)
    write_jsonl(Path(args.out)/"tcp_public_1777_1797.jsonl", out)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--years", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    main(args) 