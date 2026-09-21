#!/usr/bin/env python3
"""Restore human BibTeX keys and section-oriented formatting.

This is a one-time migration helper. It preserves legacy keys by title match
and gives records that were added afterwards concise, editable keys.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from build_publication_data import bib_entries, parse

STOP = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "the", "to", "via", "with"}
VENUES = {
    "aaai": "AAAI", "conference on computer vision and pattern": "CVPR", "cvpr": "CVPR", "iccv": "ICCV", "wacv": "WACV", "icip": "ICIP",
    "icpr": "ICPR", "acm": "ACM", "aism": "ISM", "aime": "AIME", "avss": "AVSS",
    "mipr": "MIPR", "transactions on multimedia": "TMM", "transactions on image processing": "TIP",
    "internet of things journal": "IoTJ", "journal of chemical physics": "JCP",
    "geographical information science": "IJGIS", "arxiv": "arXiv",
}


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def escape(value: str) -> str:
    return value.replace("{", "\\{").replace("}", "\\}")


def new_key(title: str, venue: str, year: str, used: set[str]) -> str:
    labelled = re.match(r"\s*([A-Za-z0-9]+(?:-[A-Za-z0-9]+)?)\s*:", title)
    words = re.findall(r"[A-Za-z0-9]+", title)
    acronym = labelled.group(1) if labelled else next((word for word in words if len(word) > 2 and word.isupper()), "")
    task_text = title.split(":", 1)[1] if labelled else title
    meaningful = [word for word in re.findall(r"[A-Za-z0-9]+", task_text) if word.lower() not in STOP and len(word) > 2]
    first = acronym or (meaningful[0] if meaningful else "Paper")
    second = next((word for word in meaningful if word.lower() != first.lower()), "Research")
    venue_key = next((short for probe, short in VENUES.items() if probe in venue.lower()), "Paper")
    base = f"{first}:{second}:{venue_key}{year}".replace(" ", "")
    key, suffix = base, 2
    while key in used:
        key = f"{base}:{suffix}"
        suffix += 1
    used.add(key)
    return key


def heading(name: str) -> list[str]:
    return ["", "%" * 78, f"%%%%%%%% {name} %%%%%%%%", "%" * 78, ""]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bib", type=Path, required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    args = parser.parse_args()

    legacy = {}
    used = set()
    for block in bib_entries(args.legacy.read_text(encoding="utf-8", errors="replace")):
        try:
            kind, key, fields = parse(block)
        except ValueError:
            # The historical file has an empty placeholder entry; it has no
            # bibliographic content to preserve or match.
            continue
        if fields.get("title"):
            legacy[normalized(fields["title"])] = key
            used.add(key)

    metadata, records = None, []
    for block in bib_entries(args.bib.read_text(encoding="utf-8")):
        kind, key, fields = parse(block)
        if fields.get("entry_role") == "site_metadata":
            metadata = (kind, key, fields)
        else:
            records.append((kind, key, fields))

    if metadata is None:
        raise ValueError("Missing site metadata entry")
    groups = {"2026 Publications": [], "2025 Publications": [], "Earlier Publications": [], "Patents & Technology Transfer": []}
    for kind, old_key, fields in records:
        title = fields.get("title", "")
        legacy_key = legacy.get(normalized(title))
        if legacy_key:
            key = legacy_key
        else:
            key = new_key(title, fields.get("venue", ""), fields.get("year", ""), used)
        if kind == "patent" or fields.get("category") == "Patents & Technology Transfer":
            group = "Patents & Technology Transfer"
        elif fields.get("year") == "2026":
            group = "2026 Publications"
        elif fields.get("year") == "2025":
            group = "2025 Publications"
        else:
            group = "Earlier Publications"
        groups[group].append((kind, key, fields))

    output = [
        "% Ming-Ching Chang publication database",
        "% Canonical source for the website. Edit this file, then run:",
        "%   python scripts/build_publication_data.py",
        "% Existing legacy keys are retained; newer entries use concise Topic:Task:VenueYear keys.",
        "",
    ]
    kind, key, fields = metadata
    output.append(f"@{kind}{{{key},")
    for name, value in fields.items():
        output.append(f"  {name} = {{{escape(value)}}},")
    output.extend(["}", ""])
    # Keep the familiar author-maintained section markers. The first three
    # sections may intentionally be empty in a given revision.
    for legacy_heading in ("Manuscripts", "Submitted Papers", "To Appear", "Ming-Ching Chang's Publication"):
        output.extend(heading(legacy_heading))
    for group in ("2026 Publications", "2025 Publications", "Earlier Publications", "Patents & Technology Transfer"):
        output.extend(heading(group))
        for kind, key, fields in sorted(groups[group], key=lambda item: item[2].get("title", "").lower()):
            output.append(f"@{kind}{{{key},")
            for name, value in fields.items():
                if value:
                    output.append(f"  {name} = {{{escape(value)}}},")
            output.extend(["}", ""])
    args.bib.write_text("\n".join(output), encoding="utf-8")
    print(f"Reformatted {len(records)} records; restored {sum(1 for _, _, f in records if normalized(f.get('title', '')) in legacy)} legacy keys.")


if __name__ == "__main__":
    main()
