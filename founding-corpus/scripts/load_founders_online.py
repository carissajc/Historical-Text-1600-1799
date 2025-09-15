import argparse, json, time, re
from pathlib import Path
from _util import load_years, in_range, session, write_jsonl, clean_text_basic
from bs4 import BeautifulSoup

def get_document_content(session, doc_url):
    """Extract content from a document page"""
    try:
        response = session.get(doc_url, timeout=60)
        if response.status_code != 200:
            return None, None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract date from metadata section (best-effort only)
        date = None
        metadata_section = soup.find('section', id='metadata')
        if metadata_section:
            date_elem = metadata_section.find('dt', string='Date')
            if date_elem and date_elem.find_next_sibling('dd'):
                date_text = date_elem.find_next_sibling('dd').get_text(strip=True)
                # Look for year patterns in date
                year_match = re.search(r'1[7-8]\d{2}', date_text)
                if year_match:
                    date = f"{year_match.group()}-01-01"
        
        # If no date in metadata, try title (best-effort only)
        if not date:
            title_elem = soup.find('title')
            if title_elem:
                title_text = title_elem.get_text()
                year_match = re.search(r'1[7-8]\d{2}', title_text)
                if year_match:
                    date = f"{year_match.group()}-01-01"
        
        # Extract main content from docbody sections
        content_parts = []
        
        # Look for document text in docbody sections
        docbody_sections = soup.find_all('div', class_='docbody')
        for section in docbody_sections:
            # Remove footnotes and references
            for elem in section.find_all(['a', 'span']):
                if 'note' in elem.get('class', []) or 'ptr' in elem.get('class', []):
                    elem.decompose()
            
            text = section.get_text(separator=' ', strip=True)
            if text and len(text) > 50:  # Filter out very short sections
                content_parts.append(text)
        
        # If no docbody, try alternative content areas
        if not content_parts:
            content_div = soup.find('section', id='doc_text')
            if content_div:
                # Remove navigation and metadata
                for elem in content_div.find_all(['nav', 'header', 'footer', 'script', 'style', 'aside']):
                    elem.decompose()
                
                text = content_div.get_text(separator=' ', strip=True)
                if text and len(text) > 200:
                    content_parts.append(text)
        
        if content_parts:
            full_text = ' '.join(content_parts)
            return date, full_text
        
        return date, None
        
    except Exception as e:
        print(f"Error processing {doc_url}: {e}")
        return None, None

def search_founders_by_year(session, year, base_url="https://founders.archives.gov"):
    """Search Founders Online for documents from a specific year"""
    print(f"  Searching year {year}...")
    
    # Try different search strategies for the year
    search_urls = [
        f"{base_url}/search?q={year}",
        f"{base_url}/search?q={year}&s=1111211111",
        f"{base_url}/search?q={year}&sa=&r=1&sr="
    ]
    
    documents = []
    
    for search_url in search_urls:
        try:
            response = session.get(search_url, timeout=60)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for document links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if '/documents/' in href and href not in [d['url'] for d in documents]:
                    title = link.get_text(strip=True)
                    if title and len(title) > 5:
                        documents.append({
                            'url': href,
                            'title': title
                        })
            
            time.sleep(0.5)  # Be respectful
            
        except Exception as e:
            print(f"    Error searching {search_url}: {e}")
            continue
    
    return documents

def explore_document_patterns(session, base_url="https://founders.archives.gov"):
    """Explore known document patterns to find documents (no date filtering)."""
    documents = []
    
    # Known document patterns for different founders
    founders = ['Adams', 'Franklin', 'Jefferson', 'Washington', 'Madison', 'Hamilton']
    
    print("Exploring Founders Online document patterns...")
    
    # Systematic search by year (broad intake)
    for year in range(1777, 1798):
        year_docs = search_founders_by_year(session, year, base_url)
        if year_docs:
            print(f"    Found {len(year_docs)} potential documents for {year}")
            # Process every discovered document (no cap)
            for doc_info in year_docs:
                doc_url = base_url + doc_info['url']
                date, text = get_document_content(session, doc_url)
                
                # Accept documents with substantial text regardless of parsed date
                if text and len(text) > 200:
                    doc_id = doc_info['url'].split('/')[-1]
                    documents.append({
                        "id": doc_id,
                        "source": "founders_online",
                        "date": (date or "1777-01-01"),
                        "license_tag": "CC-BY-NC",
                        "text": clean_text_basic(text),
                        "meta": {"title": doc_info['title'], "url": doc_url, "parsed_date": date}
                    })
                time.sleep(0.2)  # Be respectful
        time.sleep(1)  # Be respectful between years
    
    # Additional pattern exploration (kept bounded to avoid excessive 404s)
    print("\nExploring systematic document patterns...")
    for founder in founders:
        print(f"  Exploring {founder} documents...")
        for series in range(1, 10):  # Different series
            for volume in range(1, 20):  # Different volumes
                for doc in range(1, 20):  # Different documents
                    pattern = f"/documents/{founder}/{series:02d}-{volume:02d}-{doc:02d}-0001-0001"
                    doc_url = base_url + pattern
                    try:
                        date, text = get_document_content(session, doc_url)
                        if text and len(text) > 200:
                            doc_id = pattern.split('/')[-1]
                            documents.append({
                                "id": doc_id,
                                "source": "founders_online",
                                "date": (date or "1777-01-01"),
                                "license_tag": "CC-BY-NC",
                                "text": clean_text_basic(text),
                                "meta": {"founder": founder, "url": doc_url, "parsed_date": date}
                            })
                    except Exception:
                        pass
                    time.sleep(0.1)
    
    return documents

def main(args):
    # Keep args.years for CLI compatibility but we do not filter by dates anymore
    if not args.allow_nc:
        print("Skipping Founders Online (NC not allowed).")
        return
    
    s = session()
    
    # Discover and ingest all documents we can find (no date filtering)
    documents = explore_document_patterns(s)
    
    Path(args.out).mkdir(parents=True, exist_ok=True)
    write_jsonl(Path(args.out) / "founders_online_all.jsonl", documents)
    print(f"\nFounders Online: {len(documents)} documents saved (no date filtering)")
    
    # Show breakdown by parsed year if available
    year_counts = {}
    for doc in documents:
        y = (doc.get('date', '') or '1777-01-01')[:4]
        year_counts[y] = year_counts.get(y, 0) + 1
    print("\nDocuments by (parsed) year:")
    for y in sorted(year_counts.keys()):
        print(f"  {y}: {year_counts[y]} documents")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--years", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--allow-nc", action="store_true")
    args = p.parse_args()
    main(args)
