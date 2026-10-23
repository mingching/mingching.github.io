#!/usr/bin/env python3
"""Verify paper publication months from Crossref before adding BibTeX dates.

Only high-confidence exact title matches with a reported month are written.
The cache records the provider result so future refreshes do not re-query it.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from build_publication_data import bib_entries, parse


MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower().replace("{", "").replace("}", ""))


def is_paper(kind: str, fields: dict[str, str]) -> bool:
    return (
        fields.get("website_record") == "yes"
        and kind != "patent"
        and fields.get("category") != "Patents & Technology Transfer"
        and fields.get("title")
        and fields.get("year", "").isdigit()
    )


def retrieve(title: str) -> dict | None:
    url = "https://api.crossref.org/works?query.title=" + quote(title) + "&rows=5&select=title,published,published-print,published-online,issued,DOI,score"
    request = Request(url, headers={"User-Agent": "MingChingChangPublicationUpdate/1.0 (mailto:mchang2@albany.edu)"})
    with urlopen(request, timeout=20) as response:
        items = json.load(response)["message"]["items"]
    wanted = normalized(title)
    candidates = []
    for item in items:
        returned = item.get("title", [""])[0]
        ratio = SequenceMatcher(None, wanted, normalized(returned)).ratio()
        candidates.append((ratio, item))
    if not candidates:
        return None
    ratio, item = max(candidates, key=lambda item: item[0])
    if ratio < 0.91:
        return None
    for field in ("published-print", "published-online", "published", "issued"):
        parts = item.get(field, {}).get("date-parts", [[]])[0]
        if len(parts) >= 2 and 1 <= int(parts[1]) <= 12:
            year, month = int(parts[0]), int(parts[1])
            day = int(parts[2]) if len(parts) >= 3 and 1 <= int(parts[2]) <= 31 else None
            return {
                "title": item.get("title", [""])[0], "score": round(ratio, 4),
                "year": year, "month": month, "day": day, "doi": item.get("DOI", ""), "field": field,
            }
    return None


def add_date(block: str, month: int, day: int | None) -> str:
    if re.search(r"(?m)^\s*month\s*=", block):
        return block
    year_match = re.search(r"(?m)^(\s*year\s*=\s*\{\d{4}\},\s*)$", block)
    if not year_match:
        raise ValueError("Cannot locate year field")
    insertion = f"\n  month = {{{MONTHS[month - 1]}}},"
    if day:
        insertion += f"\n  date = {{{year_match.group(1).split('{')[-1][:4]}-{month:02d}-{day:02d}}},"
    return block[:year_match.end()] + insertion + block[year_match.end():]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bib", type=Path, default=Path("data/chang.bib"))
    parser.add_argument("--cache", type=Path, default=Path("data/crossref_date_cache.json"))
    parser.add_argument("--limit", type=int, default=0, help="limit uncached lookups; 0 means all")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    source = args.bib.read_text(encoding="utf-8")
    cache = json.loads(args.cache.read_text(encoding="utf-8")) if args.cache.exists() else {}
    blocks = list(bib_entries(source))
    changed = 0
    queried = 0
    updated_source = source
    for block in blocks:
        kind, key, fields = parse(block)
        if not is_paper(kind, fields) or fields.get("month"):
            continue
        record = cache.get(key)
        if record is None and (not args.limit or queried < args.limit):
            queried += 1
            try:
                record = retrieve(fields["title"])
            except Exception as error:
                record = {"error": str(error)}
            cache[key] = record
            time.sleep(0.12)
        if not record or record.get("error") or not record.get("month"):
            continue
        if int(record["year"]) != int(fields["year"]):
            continue
        replacement = add_date(block, int(record["month"]), record.get("day"))
        updated_source = updated_source.replace(block, replacement, 1)
        changed += 1
        print(f"{key}: {MONTHS[int(record['month']) - 1]} {record['year']} ({record['field']}, {record['doi']})")
    if args.write:
        args.bib.write_text(updated_source, encoding="utf-8")
        args.cache.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Verified dates added: {changed}; Crossref queries this run: {queried}.")


if __name__ == "__main__":
    main()
