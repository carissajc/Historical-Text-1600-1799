#!/usr/bin/env python3
"""
Load historical newspaper articles from Chronicling America (Library of Congress).
This provides access to thousands of real historical newspaper articles from 1777-1797.
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import requests
from _util import load_years, session


def parse_args():
    parser = argparse.ArgumentParser(description="Load Chronicling America dataset")
    parser.add_argument("--years", type=str, required=True, help="Path to years config file")
    parser.add_argument("--out", type=str, required=True, help="Output directory")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum articles per year")
    return parser.parse_args()


def search_chronicling_america(year: int, limit: int = 1000) -> List[Dict[str, Any]]:
    """Search Chronicling America for articles from a specific year."""
    base_url = "https://chroniclingamerica.loc.gov/search/pages/results/"
    
    # Search parameters for the year
    params = {
        'dateFilterType': 'yearRange',
        'date1': str(year),
        'date2': str(year),
        'searchType': 'basic',
        'language': 'English',
        'rows': min(limit, 100),  # API limit per request
        'format': 'json'
    }
    
    articles = []
    offset = 0
    
    while len(articles) < limit:
        params['start'] = offset
        
        try:
            response = session().get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if 'results' not in data:
                break
                
            results = data['results']
            if not results:
                break
                
            for result in results:
                if len(articles) >= limit:
                    break
                    
                # Extract article information
                article = {
                    'id': result.get('id', f'ca_{year}_{len(articles)}'),
                    'source': 'chronicling_america',
                    'date': f"{year}-01-01",  # We'll use year since exact dates may vary
                    'license_tag': 'CC0',  # Public domain
                    'text': result.get('ocr_eng', ''),
                    'meta': {
                        'newspaper': result.get('title', ''),
                        'headline': result.get('title_normal', ''),
                        'state': result.get('state', ''),
                        'city': result.get('city', ''),
                        'url': result.get('url', ''),
                        'page_url': result.get('url', '')
                    }
                }
                
                # Only keep articles with substantial text
                if len(article['text'].strip()) > 100:
                    articles.append(article)
            
            offset += len(results)
            
            # If we got fewer results than requested, we've reached the end
            if len(results) < params['rows']:
                break
                
            # Be respectful with API calls
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Error fetching year {year}: {e}")
            break
    
    return articles


def main():
    args = parse_args()
    start_date, end_date = load_years(args.years)
    
    print(f"Loading Chronicling America dataset for period {start_date} to {end_date}")
    
    # Extract years from the date range
    start_year = int(start_date[:4])
    end_year = int(end_date[:4])
    year_list = list(range(start_year, end_year + 1))
    
    print(f"Requesting years: {year_list}")
    print(f"Limit: {args.limit} articles per year")
    
    all_articles = []
    year_counts = {}
    
    for year in year_list:
        print(f"\nProcessing year {year}...")
        articles = search_chronicling_america(year, args.limit)
        
        year_counts[year] = len(articles)
        all_articles.extend(articles)
        
        print(f"  Found {len(articles)} articles")
        
        # Be respectful with API calls between years
        if year < end_year:
            time.sleep(1)
    
    # Save the data
    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)
    
    with open(out_path / "chronicling_america.jsonl", "w") as f:
        for record in all_articles:
            f.write(json.dumps(record) + "\n")
    
    print(f"\nTotal articles saved: {len(all_articles)}")
    print("Year breakdown:")
    for year, count in sorted(year_counts.items()):
        print(f"  {year}: {count} articles")
    
    print(f"Chronicling America data saved to {args.out}")


if __name__ == "__main__":
    main() 