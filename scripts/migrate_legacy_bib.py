#!/usr/bin/env python3
"""One-time migration: merge the legacy BibTeX file and the site catalogue.

The resulting `data/chang.bib` is intentionally the only hand-maintained
publication source.  This utility is kept for provenance; it is not used by
the production build.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def norm(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value or "")
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def entries(text: str):
    """Yield complete BibTeX entries using brace depth, not a fragile regex."""
    start = 0
    while True:
        at = text.find("@", start)
        if at < 0:
            return
        open_brace = text.find("{", at)
        if open_brace < 0:
            return
        depth = 0
        for pos in range(open_brace, len(text)):
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
                if depth == 0:
                    yield text[at : pos + 1]
                    start = pos + 1
                    break
        else:
            return


def parse_entry(block: str):
    match = re.match(r"@(\w+)\s*\{\s*([^,]+),", block, re.S)
    if not match:
        return None
    kind, key = match.groups()
    fields = {}
    body = block[match.end() : -1]
    field_re = re.compile(r"(?m)^\s*([A-Za-z][\w-]*)\s*=\s*[\{\"]")
    matches = list(field_re.finditer(body))
    for i, item in enumerate(matches):
        name = item.group(1).lower()
        value_start = item.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        value = body[value_start:end].strip().rstrip(",").strip()
        if value.endswith("}"):
            value = value[:-1]
        if value.endswith('"'):
            value = value[:-1]
        fields[name] = value.strip()
    return {"kind": kind.lower(), "key": key.strip(), "fields": fields}


def bib_value(value: str) -> str:
    return (value or "").replace("{", "\\{").replace("}", "\\}")


def make_key(title: str, year: str, used: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "", title.lower())[:42] or "publication"
    base = f"chang{year or 'undated'}{base}"
    key = base
    suffix = 2
    while key in used:
        key = f"{base}{suffix}"
        suffix += 1
    used.add(key)
    return key


def type_for(item: dict, existing: str | None) -> str:
    if existing:
        return existing
    if item.get("category") == "Patents & Technology Transfer":
        return "patent"
    venue = item.get("venue", "").lower()
    if any(word in venue for word in ("journal", "transactions", "letters", "behavior", "physics")):
        return "article"
    return "inproceedings"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-bib", type=Path, required=True)
    parser.add_argument("--site-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    legacy = {}
    for block in entries(args.legacy_bib.read_text(encoding="utf-8", errors="replace")):
        parsed = parse_entry(block)
        if parsed and parsed["fields"].get("title"):
            legacy[norm(parsed["fields"]["title"])] = parsed

    items = json.loads(args.site_json.read_text(encoding="utf-8"))
    # Preserve first occurrence of a title; title duplicates are Scholar aliases,
    # not separate papers. The canonical file keeps their richer legacy metadata.
    unique = {}
    for item in items:
        title_key = norm(item.get("title", ""))
        if title_key and title_key not in unique:
            unique[title_key] = item

    out = [
        "% Ming-Ching Chang publication database",
        "% Canonical source for the website. Edit this file, then run",
        "%   python scripts/build_publication_data.py",
        "% Do not edit generated files in _data/ directly.",
        "",
    ]
    used = set()
    for title_key, item in sorted(unique.items(), key=lambda pair: (pair[1].get("year", ""), pair[1]["title"]), reverse=True):
        old = legacy.get(title_key)
        old_fields = old["fields"] if old else {}
        year = str(item.get("year") or old_fields.get("year", ""))
        key = make_key(item["title"], year, used)
        kind = type_for(item, old["kind"] if old else None)
        fields = {
            "title": old_fields.get("title", item["title"]),
            "author": old_fields.get("author", item.get("authors", "")),
            "year": year,
            "venue": item.get("venue", old_fields.get("journal", old_fields.get("booktitle", ""))),
            "category": item.get("category", "Unclassified"),
            "scholar_url": item.get("scholar_url", ""),
            "website_record": "yes",
        }
        for name in ("journal", "booktitle", "volume", "number", "pages", "publisher", "doi", "url", "note"):
            if old_fields.get(name):
                fields[name] = old_fields[name]
        out.append(f"@{kind}{{{key},")
        for name, value in fields.items():
            if value:
                out.append(f"  {name} = {{{bib_value(value)}}},")
        out.append("}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {len(unique)} unique records to {args.output}")


if __name__ == "__main__":
    main()
