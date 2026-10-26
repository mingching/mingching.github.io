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


MONTH_NUMBERS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                 "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
MONTH_LABELS = {1: "Jan.", 2: "Feb.", 3: "Mar.", 4: "Apr.", 5: "May", 6: "Jun.",
                7: "Jul.", 8: "Aug.", 9: "Sep.", 10: "Oct.", 11: "Nov.", 12: "Dec."}
MONTH_NAMES = {1: ("jan", "january"), 2: ("feb", "february"), 3: ("mar", "march"),
               4: ("apr", "april"), 5: ("may",), 6: ("jun", "june"),
               7: ("jul", "july"), 8: ("aug", "august"), 9: ("sep", "sept", "september"),
               10: ("oct", "october"), 11: ("nov", "november"), 12: ("dec", "december")}


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


def display_text(value: str) -> str:
    """Remove BibTeX-only brace protection from text rendered on the website."""
    value = (value or "").replace("\\{", "{").replace("\\}", "}")
    return value.replace("{", "").replace("}", "").strip()


def parse_annual(value: str):
    result = []
    for pair in value.split(";"):
        year, count = pair.strip().split(":", 1)
        result.append({"year": int(year), "count": int(count)})
    return sorted(result, key=lambda item: item["year"], reverse=True)


def publication_date(fields: dict[str, str]):
    year = int(fields["year"]) if fields.get("year", "").isdigit() else 0
    month = MONTH_NUMBERS.get(fields.get("month", "").strip().lower(), 0)
    day = 0
    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", fields.get("date", "").strip())
    if match and int(match.group(1)) == year and int(match.group(2)) == month:
        day = int(match.group(3))
    if month:
        display = f"{MONTH_LABELS[month]} {day}, {year}" if day else f"{MONTH_LABELS[month]} {year}"
    else:
        display = str(year) if year else ""
    return year, month, day, display


def display_venue(venue: str, year: int, month: int) -> str:
    """Keep dates in one canonical final position, not inside the venue text."""
    if not venue or not year:
        return venue
    month_names = "|".join(name.capitalize() for name in MONTH_NAMES.get(month, ()))
    if month_names:
        venue = re.sub(
            rf",?\s*(?:{month_names})\.?\s+{year}(?=\s*(?:\([^)]*\))?\s*$)",
            "",
            venue,
            flags=re.I,
        )
    # Conference and journal exports often prefix or append the publication
    # year to the venue.  The final date display owns that year.  Preserve
    # patent application numbers such as US 2024/0123456.
    venue = re.sub(rf"(?<![\d/]){year}(?![\d/])", "", venue)
    venue = re.sub(r"\(\s*\)", "", venue)
    venue = re.sub(r"\s+,", ",", venue)
    venue = re.sub(r",\s*,+", ",", venue)
    return re.sub(r"\s{2,}", " ", venue).strip(" ,")


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
        venue = display_text(fields.get("venue", fields.get("journal", fields.get("booktitle", ""))))
        sort_year, sort_month, sort_day, date_display = publication_date(fields)
        venue = display_venue(venue, sort_year, sort_month)
        publication = {
            "key": key,
            "entry_type": kind,
            "title": display_text(title),
            "authors": display_text(fields.get("author", "")),
            "venue": venue,
            "year": fields.get("year", ""),
            "month": fields.get("month", ""),
            "date_display": date_display,
            "sort_year": sort_year,
            "sort_month": sort_month,
            "sort_day": sort_day,
            "category": fields.get("category", "Unclassified"),
            "scholar_url": fields.get("scholar_url", fields.get("url", "")),
        }
        if kind == "patent" or publication["category"] == "Patents & Technology Transfer":
            # A patent family can include both a granted right in one jurisdiction
            # and an application in another.  The canonical BibTeX may explicitly
            # record that fact; otherwise the venue wording distinguishes a formal
            # patent application from an issued patent.
            publication["patent_status"] = fields.get(
                "patent_status",
                "application" if "Patent App." in venue else "granted",
            )
            jurisdictions = []
            for country, markers in {
                "US": ("US Patent", "US20", "US "),
                "Taiwan": ("Taiwan Patent", "TWI"),
                "China": ("China Patent", "CN"),
            }.items():
                if any(marker in venue for marker in markers):
                    jurisdictions.append(country)
            publication["jurisdictions"] = fields.get("jurisdictions", ", ".join(jurisdictions))
        if fields.get("paper_url"):
            publication["paper_url"] = fields["paper_url"]
        publications.append(publication)
    if metadata is None:
        raise ValueError("Missing @misc{changWebsitePublicationStatistics,...} metadata entry")

    publications.sort(key=lambda item: (item["sort_year"], item["sort_month"], item["sort_day"], item["title"].lower()), reverse=True)
    paper_records = [item for item in publications if item["category"] != "Patents & Technology Transfer" and item["entry_type"] != "patent"]
    patent_records = [item for item in publications if item["category"] == "Patents & Technology Transfer" or item["entry_type"] == "patent"]
    journal_records = [item for item in paper_records if item["entry_type"] == "article"]
    journal_annual = Counter(
        int(item["year"])
        for item in journal_records
        if item["year"].isdigit()
    )
    annual = parse_annual(metadata["annual_totals"])
    expected_papers = int(metadata["paper_total"])
    expected_patents = int(metadata["patent_total"])
    if sum(item["count"] for item in annual) != expected_papers:
        raise ValueError("paper_total must equal the sum of annual_totals")
    if len(patent_records) != expected_patents:
        raise ValueError(f"Expected {expected_patents} patents, found {len(patent_records)}")

    catalog = {"publications": publications, "source": "data/chang.bib"}
    stats = {
        "paper_publications": expected_papers,
        "journal_publications": len(journal_records),
        "patents": expected_patents,
        "source_note": metadata.get("note", ""),
    }
    outputs = {
        args.output_dir / "bib_publications.json": json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        args.output_dir / "publication_year_counts.yml": "\n".join(f"- {{ year: {item['year']}, count: {item['count']} }}" for item in annual) + "\n",
        args.output_dir / "journal_publication_year_counts.yml": "\n".join(
            f"- {{ year: {year}, count: {count} }}"
            for year, count in sorted(journal_annual.items(), reverse=True)
        ) + "\n",
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
