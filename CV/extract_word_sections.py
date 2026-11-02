#!/usr/bin/env python3
"""One-time helper to preserve non-publication sections from a Word CV.

Usage: python extract_word_sections.py C:\\path\\to\\CV_Ming-Ching_Chang.docx
Publication entries are deliberately excluded because build_cv.py generates
those directly from chang.bib.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document


def tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#",
        "_": r"\_", "$": r"\$", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        "–": "--", "—": "---", "“": "``", "”": "''", "’": "'", "†": r"\textsuperscript{\dagger}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def render(paragraphs, start: int, end: int) -> str:
    chunks: list[str] = []
    for paragraph in paragraphs[start:end]:
        text = " ".join(paragraph.text.split())
        if not text:
            continue
        safe = tex_escape(text)
        if paragraph.style.name.startswith("Heading"):
            chunks.append(f"\\section*{{{safe}}}\n")
        else:
            chunks.append(f"\\cvitem{{{safe}}}\n")
    return "\n".join(chunks)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python extract_word_sections.py <CV.docx>")
    document = Document(sys.argv[1])
    paragraphs = document.paragraphs
    root = Path(__file__).resolve().parent
    # Word paragraph boundaries: publication material occupies 143--429.
    (root / "cv_before_publications.tex").write_text(render(paragraphs, 4, 143), encoding="utf-8")
    (root / "cv_after_publications.tex").write_text(render(paragraphs, 430, len(paragraphs)), encoding="utf-8")


if __name__ == "__main__":
    main()
