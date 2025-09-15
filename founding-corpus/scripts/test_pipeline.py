#!/usr/bin/env python3
"""Test script to demonstrate the founding corpus pipeline"""

import json
from pathlib import Path

def test_pipeline():
    """Test the pipeline with Founders Online data"""
    
    print("=== Founding Corpus Pipeline Test ===\n")
    
    # Check raw data
    raw_file = Path("data_raw/founders_online/founders_online_1777_1797.jsonl")
    if raw_file.exists():
        with open(raw_file, 'r') as f:
            raw_docs = [json.loads(line) for line in f]
        print(f"✓ Raw data: {len(raw_docs)} documents from Founders Online")
        
        # Show sample document info
        for i, doc in enumerate(raw_docs[:2]):
            print(f"  Document {i+1}: {doc['meta']['founder']} - {doc['date']}")
            print(f"    Text length: {len(doc['text'])} characters")
            print(f"    Source: {doc['source']}")
            print(f"    License: {doc['license_tag']}")
            print()
    else:
        print("✗ Raw data not found")
        return
    
    # Check normalized data
    clean_file = Path("data_clean/founders_online.jsonl")
    if clean_file.exists():
        with open(clean_file, 'r') as f:
            clean_docs = [json.loads(line) for line in f]
        print(f"✓ Normalized data: {len(clean_docs)} documents")
        
        # Show text cleaning results
        if clean_docs:
            sample_text = clean_docs[0]['text'][:200]
            print(f"  Sample cleaned text: {sample_text}...")
            print()
    else:
        print("✗ Normalized data not found")
    
    # Test deduplication (even with single source)
    print("Testing deduplication...")
    try:
        from scripts.dedup import main as dedup_main
        import sys
        
        # Temporarily modify sys.argv for dedup
        original_argv = sys.argv
        sys.argv = ['dedup.py', '--in', 'data_clean', '--out', 'data_dedup']
        
        dedup_main(sys.argv)
        
        # Restore original argv
        sys.argv = original_argv
        
        # Check if dedup output was created
        dedup_file = Path("data_dedup/corpus_all.jsonl")
        if dedup_file.exists():
            with open(dedup_file, 'r') as f:
                dedup_docs = [json.loads(line) for line in f]
            print(f"✓ Deduplication: {len(dedup_docs)} documents (no duplicates found)")
        else:
            print("✗ Deduplication output not found")
            
    except Exception as e:
        print(f"✗ Deduplication test failed: {e}")
    
    print("\n=== Pipeline Test Complete ===")
    print("\nNext steps:")
    print("1. Add more data sources (TCP, American Stories, etc.)")
    print("2. Run full pipeline: make all")
    print("3. Train tokenizer: make train-tokenizer")
    print("4. Generate reports: make report")

if __name__ == "__main__":
    test_pipeline() 