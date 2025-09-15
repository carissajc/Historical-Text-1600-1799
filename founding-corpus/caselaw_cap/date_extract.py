import regex as re
from dataclasses import dataclass
from typing import Optional, Tuple
import dateparser


MONTH_RE = r"(Jan(?:\.|uary)?|Feb(?:\.|ruary)?|Mar(?:\.|ch)?|Apr(?:\.|il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:\.|ust)?|Sep(?:\.|t\.|tember)|Oct(?:\.|ober)?|Nov(?:\.|ember)?|Dec(?:\.|ember)?)"

PATTERNS = [
    # Month name + day + year (e.g., "April 23, 1973")
    re.compile(rf"\b{MONTH_RE}\.?\s+\d{{1,2}},\s*(\d{{4}})\b", re.I),
    # Month name + day + year (e.g., "April 23 1973" - no comma)
    re.compile(rf"\b{MONTH_RE}\.?\s+\d{{1,2}}\s+(\d{{4}})\b", re.I),
    # Month name + day + year (e.g., "23 April 1973" - European format)
    re.compile(rf"\b\d{{1,2}}\s+{MONTH_RE}\.?\s+(\d{{4}})\b", re.I),
    # Month name + day + year (e.g., "23rd April 1973" - with ordinal)
    re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTH_RE}\.?\s+(\d{{4}})\b", re.I),
    # Month name + day + year (e.g., "April 23rd, 1973" - with ordinal)
    re.compile(rf"\b{MONTH_RE}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s*(\d{{4}})\b", re.I),
    # Decided/Argued with full date (e.g., "Decided April 23, 1973")
    re.compile(rf"\b(Decided|Argued)\b[^,\n]*?{MONTH_RE}\.?\s+\d{{1,2}},?\s*(\d{{4}})\b", re.I),
    # Submitted with full date (e.g., "Submitted April 16, 1973")
    re.compile(rf"\b(Submitted)\b[^,\n]*?{MONTH_RE}\.?\s+\d{{1,2}},?\s*(\d{{4}})\b", re.I),
]


@dataclass
class DateMatch:
    date_str: str
    year: Optional[int]
    offset: int


def parse_first_date(header_text: str) -> Optional[DateMatch]:
    best: Optional[DateMatch] = None
    
    for pat in PATTERNS:
        for m in pat.finditer(header_text):
            span = m.span()
            year = None
            
            # Get the year from the last capturing group
            try:
                year = int(m.group(m.lastindex)) if m.lastindex else None
            except Exception:
                year = None
            
            if not year:
                continue
            
            # Additional validation: exclude obvious false positives
            # Skip case numbers (e.g., "73-1002", "No. 73-1002")
            full_match = m.group(0)
            if re.search(r'\b(?:No\.|Case|Docket|Appeal)\s+\d{1,2}-\d{4}\b', full_match, re.I):
                continue
            
            # Skip years that are clearly case numbers (e.g., "1002" in "73-1002")
            if re.search(r'\b\d{2}-\d{4}\b', full_match):
                continue
            
            # Skip years that are too early (before 1500) or too late (after 2000)
            if year < 1500 or year > 2000:
                continue
            
            # Try to parse the full date string for better validation
            dt = None
            try:
                dt = dateparser.parse(
                    full_match,
                    settings={
                        'PREFER_DAY_OF_MONTH': 'first',
                        'PARSERS': ['absolute-time', 'relative-time', 'base-formats'],
                        'REQUIRE_PARTS': ['day', 'month', 'year']  # Require all three parts
                    }
                )
            except Exception:
                dt = None
            
            # Only accept if we can parse a valid date with all components
            if dt and dt.year == year:
                candidate = DateMatch(
                    date_str=dt.strftime('%Y-%m-%d'),
                    year=year,
                    offset=span[0]
                )
                
                # Prefer earliest offset (closest to start)
                if best is None or candidate.offset < best.offset:
                    best = candidate
    
    return best


def header_region(text: str, max_chars: int = 2000, max_lines: int = 40) -> str:
    # limit to the top of the file
    head = text[:max_chars]
    # also trim to first N lines to avoid long captions
    lines = head.splitlines()[:max_lines]
    return "\n".join(lines)

