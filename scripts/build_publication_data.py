#!/usr/bin/env python3
"""Build Jekyll publication data from the canonical BibTeX database.

Run this after editing data/chang.bib.  It writes the data files used by the
site and refuses to silently accept a malformed database.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


def bib_entries(text: str):
    start = 0
    while True:
        at = text.find("@", start)
        if at < 0:
            return
        begin = text.find("{", at)
        if begin < 0:
            raise ValueError("BibTeX entry without an opening brace")
        depth = 0
        for end in range(begin, len(text)):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    yield text[at : end + 1]
                    start = end + 1
                    break
        else:
            raise ValueError("Unclosed BibTeX entry")


def parse(block: str):
    match = re.match(r"@(\w+)\s*\{\s*([^,]+),", block, re.S)
    if not match:
        raise ValueError(f"Invalid BibTeX header: {block[:80]}")
    kind, key = match.groups()
    body = block[match.end() : -1]
    fields = {}
    field_re = re.compile(r"(?m)^\s*([A-Za-z][\w-]*)\s*=\s*[\{\"]")
    hits = list(field_re.finditer(body))
    for index, hit in enumerate(hits):
        name = hit.group(1).lower()
        tail = hits[index + 1].start() if index + 1 < len(hits) else len(body)
        value = body[hit.end() : tail].strip().rstrip(",").strip()
        if value.endswith("}") or value.endswith('"'):
            value = value[:-1]
        fields[name] = value.strip().replace("\\{", "{").replace("\\}", "}")
    return kind.lower(), key.strip(), fields


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def parse_annual(value: str):
    result = []
    for pair in value.split(";"):
        year, count = pair.strip().split(":", 1)
        result.append({"year": int(year), "count": int(count)})
    return sorted(result, key=lambda item: item["year"], reverse=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bib", type=Path, default=Path("data/chang.bib"))
    parser.add_argument("--output-dir", type=Path, default=Path("_data"))
    parser.add_argument("--check", action="store_true", help="verify outputs without writing them")
    args = parser.parse_args()

    publications = []
    metadata = None
    seen_titles = set()
    for block in bib_entries(args.bib.read_text(encoding="utf-8")):
        kind, key, fields = parse(block)
        if fields.get("entry_role") == "site_metadata":
            metadata = fields
            continue
        if fields.get("website_record") != "yes":
            continue
        title = fields.get("title", "").strip()
        if not title:
            raise ValueError(f"{key}: website record has no title")
        normalized = re.sub(r"[^a-z0-9]+", "", title.lower())
        if normalized in seen_titles:
            raise ValueError(f"Duplicate title in canonical BibTeX: {title}")
        seen_titles.add(normalized)
        publications.append({
            "key": key,
            "entry_type": kind,
            "title": title,
            "authors": fields.get("author", ""),
            "venue": fields.get("venue", fields.get("journal", fields.get("booktitle", ""))),
            "year": fields.get("year", ""),
            "category": fields.get("category", "Unclassified"),
            "scholar_url": fields.get("scholar_url", fields.get("url", "")),
        })
    if metadata is None:
        raise ValueError("Missing @misc{changWebsitePublicationStatistics,...} metadata entry")

    publications.sort(key=lambda item: (int(item["year"]) if item["year"].isdigit() else 0, item["title"].lower()), reverse=True)
    paper_records = [item for item in publications if item["category"] != "Patents & Technology Transfer" and item["entry_type"] != "patent"]
    patent_records = [item for item in publications if item["category"] == "Patents & Technology Transfer" or item["entry_type"] == "patent"]
    annual = parse_annual(metadata["annual_totals"])
    expected_papers = int(metadata["paper_total"])
    expected_patents = int(metadata["patent_total"])
    if sum(item["count"] for item in annual) != expected_papers:
        raise ValueError("paper_total must equal the sum of annual_totals")
    if len(patent_records) != expected_patents:
        raise ValueError(f"Expected {expected_patents} patents, found {len(patent_records)}")

    catalog = {"publications": publications, "source": "data/chang.bib"}
    stats = {"paper_publications": expected_papers, "patents": expected_patents, "source_note": metadata.get("note", "")}
    outputs = {
        args.output_dir / "bib_publications.json": json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        args.output_dir / "publication_year_counts.yml": "\n".join(f"- {{ year: {item['year']}, count: {item['count']} }}" for item in annual) + "\n",
        args.output_dir / "publication_stats.yml": "\n".join(f"{name}: {yaml_quote(str(value))}" for name, value in stats.items()) + "\n",
    }
    stale = []
    for path, text in outputs.items():
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            stale.append(path)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    if args.check and stale:
        raise SystemExit("Generated publication data is stale: " + ", ".join(map(str, stale)))
    print(f"Validated {len(publications)} BibTeX records; {expected_papers} paper publications and {expected_patents} patents are published on the site.")


if __name__ == "__main__":
    main()
