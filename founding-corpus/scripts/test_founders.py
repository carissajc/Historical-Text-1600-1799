#!/usr/bin/env python3
"""Quick test script for Founders Online content extraction"""

import requests
from bs4 import BeautifulSoup
import re

def test_document_extraction():
    """Test extracting content from a few known documents"""
    
    # Test with a few known document URLs
    test_urls = [
        "https://founders.archives.gov/documents/Adams/01-01-02-0001-0001",
        "https://founders.archives.gov/documents/Franklin/01-01-02-0001-0001",
        "https://founders.archives.gov/documents/Jefferson/01-01-02-0001-0001"
    ]
    
    session = requests.Session()
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            response = session.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Get title
                title = soup.find('title')
                if title:
                    print(f"Title: {title.get_text()}")
                    
                    # Look for year in title
                    year_match = re.search(r'1[7-8]\d{2}', title.get_text())
                    if year_match:
                        print(f"Year found: {year_match.group()}")
                
                # Look for content
                content_div = soup.find('div', class_='document-content') or soup.find('div', id='content')
                if content_div:
                    text = content_div.get_text(strip=True)
                    print(f"Content length: {len(text)} characters")
                    print(f"First 200 chars: {text[:200]}...")
                else:
                    print("No content div found")
                    
            else:
                print(f"HTTP {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_document_extraction() 