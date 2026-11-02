#!/usr/bin/env python3
"""Generate CV publication sections from the canonical chang.bib file.

The generated_publications.tex file is intentionally not hand-edited. Edit
chang.bib, then run this script and compile main.tex.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BIB = ROOT / "chang.bib"
OUT = ROOT / "generated_publications.tex"

MONTHS = {
    "jan": (1, "Jan."), "feb": (2, "Feb."), "mar": (3, "Mar."),
    "apr": (4, "Apr."), "may": (5, "May"), "jun": (6, "Jun."),
    "jul": (7, "Jul."), "aug": (8, "Aug."), "sep": (9, "Sep."),
    "oct": (10, "Oct."), "nov": (11, "Nov."), "dec": (12, "Dec."),
}


def latex(text: str) -> str:
    """Escape BibTeX/plain-text fields for ordinary LaTeX prose."""
    # The canonical BibTeX file uses braces to protect capitalization and has
    # a few legacy TeX accent/protection commands. Convert those to ordinary
    # Unicode/plain text before escaping the field for this generated output.
    text = text.replace(r'\"{o}', 'ö').replace(r'\"o', 'ö')
    text = text.replace(r'\&', '&')
    text = text.replace(r'\{', '{').replace(r'\}', '}')
    text = re.sub(r"\\([A-Za-z])", r"\1", text)
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#",
        "_": r"\_", "$": r"\$", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        "–": "--", "—": "---", "“": "``", "”": "''", "’": "'", "†": r"\textsuperscript{\dagger}",
    }
    text = text.replace("{", "").replace("}", "")
    return "".join(replacements.get(ch, ch) for ch in text).replace("…", r"\ldots{}")


def fields(block: str) -> dict[str, str]:
    result: dict[str, str] = {}
    pos = 0
    matcher = re.compile(r"(?m)^\s*([A-Za-z_]+)\s*=\s*\{")
    while (match := matcher.search(block, pos)):
        key = match.group(1).lower()
        start = match.end()
        depth, end = 1, start
        while end < len(block) and depth:
            if block[end] == "{":
                depth += 1
            elif block[end] == "}":
                depth -= 1
            end += 1
        result[key] = block[start:end - 1].strip()
        pos = end
    return result


def entries(text: str) -> list[dict[str, str]]:
    starts = list(re.finditer(r"(?m)^@(article|inproceedings|phdthesis|patent|book|inbook)\s*\{([^,]+),", text))
    result = []
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        item = fields(text[match.end():end])
        item["entrytype"] = match.group(1).lower()
        item["key"] = match.group(2)
        if item.get("website_record", "yes").lower() != "no":
            result.append(item)
    return result


def initial(given: str) -> str:
    pieces = []
    for part in re.split(r"[-\s]+", given.strip()):
        if not part:
            continue
        pieces.append(part[0].upper() + ".")
    return "-".join(pieces)


def author_name(name: str) -> str:
    name = name.strip()
    if name == "...":
        return r"\ldots{}"
    if "," in name:
        surname, given = [part.strip() for part in name.split(",", 1)]
    else:
        parts = name.split()
        if len(parts) == 1:
            return latex(name)
        surname, given = parts[-1], " ".join(parts[:-1])
    rendered = f"{initial(given)} {latex(surname)}"
    normalized = re.sub(r"[^a-z]", "", name.lower())
    if normalized in {"mingchingchang", "mcchang"}:
        return r"\underline{M.-C. Chang}"
    return rendered


def authors(value: str) -> str:
    names = [author_name(name) for name in re.split(r"\s+and\s+", value) if name.strip()]
    if len(names) <= 1:
        return "".join(names)
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def date_key(item: dict[str, str]) -> tuple[int, int, int]:
    year = int(re.search(r"\d{4}", item.get("year", "0")).group() if re.search(r"\d{4}", item.get("year", "")) else 0)
    if re.match(r"\d{4}-\d{2}-\d{2}", item.get("date", "")):
        _, month, day = item["date"].split("-")
        return year, int(month), int(day)
    return year, MONTHS.get(item.get("month", "").lower()[:3], (0, ""))[0], 0


def date_text(item: dict[str, str]) -> str:
    year = item.get("year", "").strip()
    full = item.get("date", "").strip()
    if re.match(r"\d{4}-\d{2}-\d{2}", full):
        y, m, d = full.split("-")
        return f"{MONTHS.get(MONTHS_BY_NUMBER[int(m)], (0, m))[1]} {int(d)}, {y}"
    short = item.get("month", "").lower()[:3]
    if short in MONTHS:
        return f"{MONTHS[short][1]} {year}"
    return year


MONTHS_BY_NUMBER = {number: key for key, (number, _) in MONTHS.items()}


def venue_and_date(item: dict[str, str]) -> str:
    venue = latex(item.get("venue", item.get("journal", ""))).strip()
    date = date_text(item)
    year = item.get("year", "").strip()
    if item.get("month") or item.get("date"):
        venue = re.sub(r",?\s*" + re.escape(year) + r"(?:\s*\([^)]*\))?\s*$", "", venue).rstrip(" ,")
        return rf"\emph{{{venue}}}, {date}" if venue else date
    return rf"\emph{{{venue}}}" if venue else date


def citation(item: dict[str, str]) -> str:
    title = latex(item.get("title", "Untitled"))
    details = venue_and_date(item)
    link = item.get("paper_url") or item.get("url")
    suffix = rf" \href{{{link}}}{{[PDF/link]}}" if link and link.startswith(("http://", "https://")) else ""
    return f"{authors(item.get('author', ''))}, ``{title},'' {details}.{suffix}"


def write_group(handle, title: str, records: list[dict[str, str]], note: bool = False) -> None:
    handle.write(f"\\section*{{{title}}}\n")
    if note:
        handle.write("\\pubnote\n")
    handle.write("\\begin{publist}\n")
    for item in sorted(records, key=date_key, reverse=True):
        handle.write("  \\item " + citation(item) + "\n")
    handle.write("\\end{publist}\n")


def main() -> None:
    records = entries(BIB.read_text(encoding="utf-8"))
    groups = {
        "Referred Journal Publications": [item for item in records if item["entrytype"] == "article"],
        "Peer-Reviewed Conference and Workshop Publications": [item for item in records if item["entrytype"] == "inproceedings"],
        "Thesis": [item for item in records if item["entrytype"] == "phdthesis"],
        "Patents": [item for item in records if item["entrytype"] == "patent"],
    }
    with OUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("% Auto-generated by build_cv.py from chang.bib. Do not edit directly.\n\n")
        write_group(handle, "Referred Journal Publications", groups["Referred Journal Publications"], note=True)
        write_group(handle, "Peer-Reviewed Conference and Workshop Publications", groups["Peer-Reviewed Conference and Workshop Publications"], note=True)
        write_group(handle, "Thesis", groups["Thesis"])
        write_group(handle, "Patents", groups["Patents"])
    print("Generated", OUT.name, "from", len(records), "BibTeX records.")


if __name__ == "__main__":
    main()
