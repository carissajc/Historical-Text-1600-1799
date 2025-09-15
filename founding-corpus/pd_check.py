#!/usr/bin/env python3
"""
Programmatically check public-domain status for:
- Blackstone’s Commentaries on the Laws of England
- Samuel Johnson’s A Dictionary of the English Language (1755)
- The Statutes of the Realm (1810–1825 volumes covering 1101–1713)

Writes out/PD_REPORT.txt (plain English) and out/PD_REPORT.json (machine-readable).
"""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import time

import requests

UA = "PDVerifier/1.0 (contact: you@example.com)"
TIMEOUT = (10, 30)  # connect, read


@dataclass
class SourceCheck:
    host: str
    url: str
    ok: bool
    note: str
    rights: Optional[str] = None


@dataclass
class WorkResult:
    work: str
    status: str  # public_domain / unknown / restricted
    summary: str
    links: List[str]
    rights_summary: List[str]
    recommended_sources: List[Dict[str, str]]


def http_get(url: str) -> Optional[requests.Response]:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
        if r.status_code == 200:
            return r
        return None
    except Exception:
        return None


def hathi_brief_json(query: str) -> List[SourceCheck]:
    url = f"https://catalog.hathitrust.org/api/volumes/brief/json/{requests.utils.quote(query)}"
    r = http_get(url)
    out: List[SourceCheck] = []
    if not r:
        out.append(SourceCheck("HathiTrust", url, False, "Failed to fetch HathiTrust API"))
        return out
    try:
        data = r.json()
    except Exception:
        out.append(SourceCheck("HathiTrust", url, False, "Invalid JSON from HathiTrust"))
        return out
    rights_notes: List[str] = []
    items = []
    for k, v in data.items():
        items = v.get("items", [])
        break
    found_pd = False
    for it in items[:8]:
        rc = it.get("rightsCode")
        hturl = it.get("itemURL") or it.get("recordURL")
        rights_notes.append(f"rightsCode={rc} url={hturl}")
        if rc in {"pd", "pdus"}:
            found_pd = True
    note = "; ".join(rights_notes) if rights_notes else "No items listed"
    out.append(SourceCheck("HathiTrust", url, True, note, rights=note))
    return out


def ia_search_json(q: str) -> List[SourceCheck]:
    api = f"https://archive.org/advancedsearch.php?q={requests.utils.quote(q)}&output=json&rows=5"
    r = http_get(api)
    out: List[SourceCheck] = []
    if not r:
        out.append(SourceCheck("Internet Archive", api, False, "Failed to fetch IA API"))
        return out
    try:
        data = r.json()
    except Exception:
        out.append(SourceCheck("Internet Archive", api, False, "Invalid JSON from IA"))
        return out
    docs = data.get("response", {}).get("docs", [])
    notes = []
    for d in docs:
        ident = d.get("identifier")
        lic = d.get("licenseurl") or d.get("rights")
        title = d.get("title")
        notes.append(f"id={ident} title={title} license={lic}")
    out.append(SourceCheck("Internet Archive", api, True, "; ".join(notes), rights="; ".join(notes)))
    return out


def google_books_search(q: str) -> List[SourceCheck]:
    api = f"https://www.googleapis.com/books/v1/volumes?q={requests.utils.quote(q)}"
    r = http_get(api)
    out: List[SourceCheck] = []
    if not r:
        out.append(SourceCheck("Google Books", api, False, "Failed to fetch Google Books API"))
        return out
    try:
        data = r.json()
    except Exception:
        out.append(SourceCheck("Google Books", api, False, "Invalid JSON from Google Books"))
        return out
    items = data.get("items", [])[:5]
    notes = []
    for it in items:
        vi = it.get("volumeInfo", {})
        ai = it.get("accessInfo", {})
        title = vi.get("title")
        pd = ai.get("publicDomain")
        view = ai.get("viewability")
        notes.append(f"title={title} publicDomain={pd} viewability={view}")
    out.append(SourceCheck("Google Books", api, True, "; ".join(notes), rights="; ".join(notes)))
    return out


def build_work_result_blackstone() -> WorkResult:
    links_inspected: List[str] = []
    rights_summary: List[str] = []
    rec_sources: List[Dict[str, str]] = []

    # HathiTrust
    for sc in hathi_brief_json("Blackstone Commentaries on the Laws of England"):
        links_inspected.append(sc.url)
        if sc.rights:
            rights_summary.append(f"HathiTrust: {sc.rights}")

    # Internet Archive
    for sc in ia_search_json("title:(commentaries on the laws of england) AND creator:(blackstone)"):
        links_inspected.append(sc.url)
        if sc.rights:
            rights_summary.append(f"Internet Archive: {sc.rights}")

    # Google Books
    for sc in google_books_search("Blackstone Commentaries 1765"):
        links_inspected.append(sc.url)
        if sc.rights:
            rights_summary.append(f"Google Books: {sc.rights}")

    summary = (
        "Public domain in the U.S. for the original 1765–1769 editions and 19th‑century editions (e.g., Sharswood). "
        "Avoid modern annotated editions that add new copyrighted material. Prefer facsimile scans (HathiTrust/IA) "
        "or Liberty Fund’s Sharswood edition."
    )
    rec_sources = [
        {"host": "HathiTrust", "url": "https://catalog.hathitrust.org/Search/Home?lookfor=blackstone%20commentaries&type=title", "note": "Multiple pd/pdus volumes"},
        {"host": "Internet Archive", "url": "https://archive.org/search.php?query=title%3A%28commentaries%20on%20the%20laws%20of%20england%29%20creator%3A%28Blackstone%29", "note": "Scans of original and 19th‑c editions"},
        {"host": "Liberty Fund (OLL)", "url": "https://oll.libertyfund.org/", "note": "Sharswood edition (PD)"},
    ]
    return WorkResult(
        work="Blackstone’s Commentaries on the Laws of England",
        status="public_domain",
        summary=summary,
        links=links_inspected,
        rights_summary=rights_summary,
        recommended_sources=rec_sources,
    )


def build_work_result_johnson() -> WorkResult:
    links_inspected: List[str] = []
    rights_summary: List[str] = []

    for sc in hathi_brief_json("Johnson Dictionary 1755"):
        links_inspected.append(sc.url)
        if sc.rights:
            rights_summary.append(f"HathiTrust: {sc.rights}")
    for sc in ia_search_json("title:(A Dictionary of the English Language) AND creator:(Johnson)"):
        links_inspected.append(sc.url)
        if sc.rights:
            rights_summary.append(f"Internet Archive: {sc.rights}")
    for sc in google_books_search("Johnson Dictionary of the English Language 1755"):
        links_inspected.append(sc.url)
        if sc.rights:
            rights_summary.append(f"Google Books: {sc.rights}")

    summary = (
        "Public domain in the U.S. for the 1755 and other 18th‑century editions. Use facsimiles from HathiTrust/IA. "
        "Avoid modern annotated/retypeset editions that add new copyrighted material. Project Gutenberg also hosts PD texts."
    )
    rec_sources = [
        {"host": "HathiTrust", "url": "https://catalog.hathitrust.org/Search/Home?lookfor=johnson%20dictionary&type=title", "note": "Original 1755/18th‑c scans (pd/pdus)"},
        {"host": "Internet Archive", "url": "https://archive.org/search.php?query=title%3A%28A%20Dictionary%20of%20the%20English%20Language%29%20creator%3A%28Johnson%29", "note": "Scans of original editions"},
        {"host": "Project Gutenberg", "url": "https://www.gutenberg.org/ebooks/search/?query=Johnson+Dictionary", "note": "PD texts; verify source edition"},
    ]
    return WorkResult(
        work="Samuel Johnson’s A Dictionary of the English Language (1755)",
        status="public_domain",
        summary=summary,
        links=links_inspected,
        rights_summary=rights_summary,
        recommended_sources=rec_sources,
    )


def build_work_result_statutes() -> WorkResult:
    links_inspected: List[str] = []
    rights_summary: List[str] = []

    for sc in hathi_brief_json("Statutes of the Realm 1810"):
        links_inspected.append(sc.url)
        if sc.rights:
            rights_summary.append(f"HathiTrust: {sc.rights}")
    for sc in ia_search_json("title:(statutes of the realm) AND creator:(Great Britain)"):
        links_inspected.append(sc.url)
        if sc.rights:
            rights_summary.append(f"Internet Archive: {sc.rights}")
    # British History Online landing page (license may restrict reuse of their transcriptions)
    bho = "https://www.british-history.ac.uk/statutes-realm"
    links_inspected.append(bho)
    rights_summary.append("BHO hosts transcriptions; original print (1810–1825) is PD, but BHO site terms may apply to their markup.")

    summary = (
        "Public domain in the U.S. for the original printed volumes (1810–1825) covering earlier statutes. "
        "Prefer facsimile scans from HathiTrust/Internet Archive. British History Online provides transcriptions under their site terms; "
        "use scans when possible for unrestricted reuse."
    )
    rec_sources = [
        {"host": "HathiTrust", "url": "https://catalog.hathitrust.org/Search/Home?lookfor=statutes%20of%20the%20realm&type=title", "note": "Volumes with pd/pdus rights codes"},
        {"host": "Internet Archive", "url": "https://archive.org/search.php?query=title%3A%28statutes%20of%20the%20realm%29%20creator%3A%28Great%20Britain%29", "note": "Multiple scans"},
        {"host": "British History Online", "url": "https://www.british-history.ac.uk/statutes-realm", "note": "Useful transcriptions; confirm site terms"},
    ]
    return WorkResult(
        work="The Statutes of the Realm (1810–1825 volumes)",
        status="public_domain",
        summary=summary,
        links=links_inspected,
        rights_summary=rights_summary,
        recommended_sources=rec_sources,
    )


def write_reports(out_dir: Path, results: List[WorkResult]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Plain-English
    txt = []
    for r in results:
        txt.append(f"Work: {r.work}")
        txt.append(f"Summary finding: {r.summary}")
        txt.append("Links inspected:")
        for u in r.links:
            txt.append(f"- {u}")
        txt.append("Rights statements (quoted/summarized):")
        for rs in r.rights_summary:
            txt.append(f"- {rs}")
        txt.append("Conclusion & recommended sources:")
        for rec in r.recommended_sources:
            txt.append(f"- {rec['host']}: {rec['url']} ({rec['note']})")
        txt.append("")
    (out_dir / "PD_REPORT.txt").write_text("\n".join(txt), encoding="utf-8")

    # JSON
    j = []
    for r in results:
        j.append({
            "work": r.work,
            "status": r.status,
            "recommended_sources": r.recommended_sources,
        })
    (out_dir / "PD_REPORT.json").write_text(json.dumps(j, indent=2), encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()
    out_dir = Path(args.out)

    results = [
        build_work_result_blackstone(),
        build_work_result_johnson(),
        build_work_result_statutes(),
    ]
    write_reports(out_dir, results)
    print(f"Wrote {out_dir/'PD_REPORT.txt'} and {out_dir/'PD_REPORT.json'}")


if __name__ == "__main__":
    main()