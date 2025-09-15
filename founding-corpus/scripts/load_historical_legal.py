#!/usr/bin/env python3
"""
Load historical legal documents from publicly available sources.
This provides access to foundational legal texts from the founding period.
"""

import argparse
from pathlib import Path
from _util import write_jsonl, clean_text_basic

# Sample historical legal documents (these would normally be fetched from APIs)
HISTORICAL_LEGAL_TEXTS = [
    {
        "id": "constitution_preamble",
        "source": "historical_legal",
        "date": "1787-09-17",
        "license_tag": "PublicDomain",
        "text": """We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defence, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.""",
        "meta": {
            "document_type": "constitution",
            "title": "Constitution of the United States - Preamble",
            "description": "The opening statement of the U.S. Constitution"
        }
    },
    {
        "id": "declaration_independence",
        "source": "historical_legal",
        "date": "1776-07-04",
        "license_tag": "PublicDomain",
        "text": """When in the Course of human events, it becomes necessary for one people to dissolve the political bands which have connected them with another, and to assume among the powers of the earth, the separate and equal station to which the Laws of Nature and of Nature's God entitle them, a decent respect to the opinions of mankind requires that they should declare the causes which impel them to the separation. We hold these truths to be self-evident, that all men are created equal, that they are endowed by their Creator with certain unalienable Rights, that among these are Life, Liberty and the pursuit of Happiness.""",
        "meta": {
            "document_type": "declaration",
            "title": "Declaration of Independence - Opening",
            "description": "The opening paragraphs of the Declaration of Independence"
        }
    },
    {
        "id": "federalist_1",
        "source": "historical_legal",
        "date": "1787-10-27",
        "license_tag": "PublicDomain",
        "text": """After an unequivocal experience of the inefficiency of the subsisting federal government, you are called upon to deliberate on a new Constitution for the United States of America. The subject speaks its own importance; comprehending in its consequences nothing less than the existence of the UNION, the safety and welfare of the parts of which it is composed, the fate of an empire in many respects the most interesting in the world. It has been frequently remarked that it seems to have been reserved to the people of this country, by their conduct and example, to decide the important question, whether societies of men are really capable or not of establishing good government from reflection and choice, or whether they are forever destined to depend for their political constitutions on accident and force.""",
        "meta": {
            "document_type": "federalist_paper",
            "title": "Federalist No. 1 - Opening",
            "author": "Alexander Hamilton",
            "description": "The opening of the first Federalist Paper"
        }
    },
    {
        "id": "bill_of_rights_1",
        "source": "historical_legal",
        "date": "1789-09-25",
        "license_tag": "PublicDomain",
        "text": """Congress shall make no law respecting an establishment of religion, or prohibiting the free exercise thereof; or abridging the freedom of speech, or of the press; or the right of the people peaceably to assemble, and to petition the Government for a redress of grievances.""",
        "meta": {
            "document_type": "amendment",
            "title": "First Amendment to the U.S. Constitution",
            "description": "The First Amendment protecting freedom of speech, religion, press, assembly, and petition"
        }
    },
    {
        "id": "articles_confederation",
        "source": "historical_legal",
        "date": "1781-03-01",
        "license_tag": "PublicDomain",
        "text": """To all to whom these Presents shall come, we, the undersigned Delegates of the States affixed to our Names send greeting. Whereas the Delegates of the United States of America in Congress assembled did on the fifteenth day of November in the year of our Lord One Thousand Seven Hundred and Seventy seven, and in the Second Year of the independence of America agree to certain articles of Confederation and perpetual Union between the States of Newhampshire, Massachusetts-bay, Rhodeisland and Providence Plantations, Connecticut, New York, New Jersey, Pennsylvania, Delaware, Maryland, Virginia, North Carolina, South Carolina and Georgia.""",
        "meta": {
            "document_type": "articles_of_confederation",
            "title": "Articles of Confederation - Opening",
            "description": "The opening of the Articles of Confederation, the first constitution of the United States"
        }
    }
]

def main(args):
    print(f"Loading {len(HISTORICAL_LEGAL_TEXTS)} historical legal documents")
    
    # Filter documents by date range if needed
    start_year = int(args.start_year) if args.start_year else 1777
    end_year = int(args.end_year) if args.end_year else 1797
    
    filtered_docs = []
    for doc in HISTORICAL_LEGAL_TEXTS:
        doc_year = int(doc["date"][:4])
        if start_year <= doc_year <= end_year:
            filtered_docs.append(doc)
    
    print(f"Documents in range {start_year}-{end_year}: {len(filtered_docs)}")
    
    Path(args.out).mkdir(parents=True, exist_ok=True)
    write_jsonl(Path(args.out)/"historical_legal_1777_1797.jsonl", filtered_docs)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--start-year", default="1777", help="Start year for filtering")
    p.add_argument("--end-year", default="1797", help="End year for filtering")
    p.add_argument("--out", required=True, help="Output directory")
    args = p.parse_args()
    main(args) 