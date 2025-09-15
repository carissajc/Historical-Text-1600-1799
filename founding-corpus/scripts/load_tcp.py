#!/usr/bin/env python3
"""
Load TCP (Text Creation Partnership) data from Evans and ECCO collections.
Optimized for speed with parallel processing and efficient XML parsing.
"""

import argparse
import zipfile
import re
import io
import time
from pathlib import Path
from lxml import etree
from _util import load_years, in_range, write_jsonl, clean_text_basic
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_date_from_xml_fast(xml_content, corpus_name):
    """Fast date extraction using regex instead of full XML parsing."""
    try:
        # Use regex to find date patterns - much faster than XML parsing
        xml_str = xml_content.decode('utf-8', errors='ignore')
        
        # Look for date in SOURCEDESC section first (most reliable for both Evans and ECCO)
        sourcedesc_match = re.search(r'<SOURCEDESC[^>]*>.*?<DATE>([^<]+)</DATE>', xml_str, re.DOTALL)
        if sourcedesc_match:
            date_text = sourcedesc_match.group(1).strip()
            year_match = re.search(r'(\d{4})', date_text)
            if year_match:
                return int(year_match.group(1))
        
        # For Evans: look for date in title
        if corpus_name == "evans":
            title_match = re.search(r'<TITLE[^>]*TYPE="alt"[^>]*>.*?(\d{4})', xml_str, re.DOTALL)
            if title_match:
                return int(title_match.group(1))
        
        # For ECCO: look for date in title page text
        if corpus_name == "ecco":
            title_page_match = re.search(r'<DIV1 TYPE="title page">.*?(\d{4})', xml_str, re.DOTALL)
            if title_page_match:
                return int(title_page_match.group(1))
        
        # Fallback: look for any 4-digit year in the header (but filter carefully)
        header_match = re.search(r'<HEADER>.*?(\d{4})', xml_str, re.DOTALL)
        if header_match:
            year = int(header_match.group(1))
            # Filter out modern years (2000+) and TCP processing years
            if year < 2000 and year > 1500:
                return year
        
        return None
    except Exception:
        return None

def extract_text_from_xml_fast(xml_content):
    """Fast text extraction using regex instead of full XML parsing."""
    try:
        xml_str = xml_content.decode('utf-8', errors='ignore')
        
        # Extract text from TEXT section
        text_match = re.search(r'<TEXT[^>]*>(.*?)</TEXT>', xml_str, re.DOTALL)
        if not text_match:
            return None
        
        text_section = text_match.group(1)
        
        # Remove XML tags but keep text content
        text = re.sub(r'<[^>]+>', ' ', text_section)
        
        # Clean up whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text if len(text) > 100 else None
        
    except Exception:
        return None

def process_xml_file_fast(zip_file, xml_file, start_year, end_year, corpus_name):
    """Process a single XML file quickly."""
    try:
        with zip_file.open(xml_file) as f:
            xml_content = f.read()
        
        # Fast date extraction
        year = extract_date_from_xml_fast(xml_content, corpus_name)
        if year is None:
            return None
        if year < start_year or year > end_year:
            return None
        
        # Fast text extraction
        text = extract_text_from_xml_fast(xml_content)
        if not text or len(text) < 100:
            return None
        
        # Create document record
        doc_id = xml_file.replace('.xml', '').replace('/', '_')
        doc = {
            'id': doc_id,
            'source': f'{corpus_name}_tcp',
            'date': f'{year}-01-01',
            'license_tag': 'PublicDomain',
            'text': clean_text_basic(text),
            'meta': {
                'corpus': corpus_name,
                'xml_file': xml_file,
                'year': year
            }
        }
        
        return doc
        
    except Exception as e:
        print(f"Error processing {xml_file}: {e}")
        return None

def process_nested_zip_fast(main_zip_path, start_year, end_year, corpus_name, max_workers=4):
    """Process nested zip structure efficiently."""
    documents = []
    
    try:
        with zipfile.ZipFile(main_zip_path, 'r') as main_zip:
            # Find nested zip files (ignore unedited.zip)
            nested_zips = [f for f in main_zip.namelist() 
                          if f.endswith('.zip') and 'unedited' not in f]
            
            print(f"Found {len(nested_zips)} nested zip files in {main_zip_path.name}")
            
            for nested_zip_name in nested_zips:
                print(f"Processing nested zip: {nested_zip_name}")
                
                # Extract nested zip to memory
                nested_zip_data = main_zip.read(nested_zip_name)
                
                with zipfile.ZipFile(io.BytesIO(nested_zip_data)) as nested_zip:
                    xml_files = [f for f in nested_zip.namelist() if f.endswith('.xml')]
                    
                    print(f"  Found {len(xml_files)} XML files in {nested_zip_name}")
                    
                    # Process XML files in parallel
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = []
                        for xml_file in xml_files:
                            future = executor.submit(
                                process_xml_file_fast, 
                                nested_zip, xml_file, start_year, end_year, corpus_name
                            )
                            futures.append(future)
                        
                        # Collect results
                        extracted_count = 0
                        for future in as_completed(futures):
                            result = future.result()
                            if result:
                                documents.append(result)
                                extracted_count += 1
                    
                    print(f"  Extracted {extracted_count} documents from {nested_zip_name}")
                    
    except Exception as e:
        print(f"Error processing main zip {main_zip_path}: {e}")
    
    return documents

def main(args):
    start_date, end_date = load_years(args.years)
    start_year = int(start_date[:4])
    end_year = int(end_date[:4])
    
    print(f"Loading {args.corpus} TCP data for {start_year}-{end_year}")
    print("Using optimized fast processing...")
    
    base = Path(args.out)
    base.mkdir(parents=True, exist_ok=True)
    
    # Find main zip files
    zip_files = list(base.glob("*.zip"))
    if not zip_files:
        print(f"No zip files found in {base}")
        return
    
    print(f"Found {len(zip_files)} main zip files")
    
    all_documents = []
    start_time = time.time()
    
    # Process each main zip file
    for zip_file in zip_files:
        print(f"\nProcessing {zip_file.name}")
        documents = process_nested_zip_fast(zip_file, start_year, end_year, args.corpus)
        all_documents.extend(documents)
        print(f"Total documents so far: {len(all_documents)}")
    
    end_time = time.time()
    print(f"\nExtraction completed in {end_time - start_time:.2f} seconds")
    print(f"Total documents extracted: {len(all_documents)}")
    
    # Write output
    output_file = base / f"{args.corpus}_tcp_{start_year}_{end_year}.jsonl"
    write_jsonl(output_file, all_documents)
    print(f"Wrote {len(all_documents)} documents to {output_file}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", required=True, choices=["evans", "ecco"])
    p.add_argument("--years", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    main(args)
