#!/usr/bin/env python3
"""Apply the CV's title-style capitalization to website paper titles.

BibTeX braces continue to protect acronyms and intentional capitalization.
Run without ``--write`` to preview; run with it before rebuilding site data.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from build_publication_data import bib_entries, parse


MINOR_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "if", "in",
    "into", "nor", "of", "on", "or", "over", "per", "the", "to", "up", "via",
    "vs", "with", "within", "without",
}
ACRONYMS = {
    "ai": "AI", "api": "API", "atm": "ATM", "avss": "AVSS", "ckks": "CKKS",
    "cnn": "CNN", "cfo": "CFO", "cvpr": "CVPR", "dce": "DCE", "dnn": "DNN",
    "eot": "EOT", "fhew": "FHEW", "gan": "GAN", "gpu": "GPU", "hbm": "HBM",
    "icip": "ICIP", "icml": "ICML", "ieee": "IEEE", "ijcv": "IJCV", "io": "IO",
    "clip": "CLIP", "llm": "LLM", "llms": "LLMs", "lvlm": "LVLM", "mipr": "MIPR",
    "mri": "MRI", "mllm": "MLLM", "mllms": "MLLMs", "papr": "PAPR", "plsa": "PLSA",
    "nvidia": "NVIDIA", "pcb": "PCB", "por": "POR", "ptz": "PTZ", "rag": "RAG", "rl": "RL",
    "rnn": "RNN", "tfhe": "TFHE", "uav": "UAV",
    "vot": "VOT", "yolo": "YOLO",
}
NAME_CASE = {
    "Deeppvmap": "DeepPVMap", "Flashsinkhorn": "FlashSinkhorn", "Msqnet": "MSQNet",
    "Nas": "NAS", "RlmInistyler": "RLMiniStyler", "Rlministyler": "RLMiniStyler",
    "Smiletrack": "SMILEtrack", "TextSleuth": "TextSleuth", "Transrpn": "TransRPN",
    "Uu": "UU", "Uu-mamba": "UU-Mamba", "Vocbench": "VocBench",
}


def title_word(word: str, position: int, final: bool, force_capitalize: bool = False) -> str:
    pieces = re.split(r"(-)", word)
    result = []
    for piece in pieces:
        if piece == "-":
            result.append(piece)
            continue
        key = piece.lower()
        if key in ACRONYMS:
            result.append(ACRONYMS[key])
        elif piece in NAME_CASE:
            result.append(NAME_CASE[piece])
        elif any(char.isupper() for char in piece[1:]) or any(char.isdigit() for char in piece):
            result.append(piece)
        elif position > 0 and not final and not force_capitalize and key in MINOR_WORDS:
            result.append(key)
        else:
            result.append(piece[:1].upper() + piece[1:].lower())
    return "".join(result)


def title_case(value: str) -> str:
    # Brace-protected content is intentional BibTeX capitalization and remains
    # untouched. Process only text outside braces.
    protected = re.split(r"(\{[^{}]*\})", value)
    word_pattern = r"\d+(?:st|nd|rd|th)|[A-Za-z]+(?:'[A-Za-z]+)?"
    total_words = re.findall(word_pattern, re.sub(r"\{[^{}]*\}", "", value), flags=re.I)
    word_count = 0
    for index, part in enumerate(protected):
        if part.startswith("{") and part.endswith("}"):
            continue
        def replace(match):
            nonlocal word_count
            word_count += 1
            prior = part[:match.start()].rstrip()
            after_colon = bool(prior and prior[-1] in ":—–")
            return title_word(match.group(0), word_count - 1, word_count == len(total_words), after_colon)
        protected[index] = re.sub(word_pattern, replace, part, flags=re.I)
    return "".join(protected)


def is_paper(kind: str, fields: dict[str, str]) -> bool:
    return (
        fields.get("website_record") == "yes"
        and kind != "patent"
        and fields.get("category") != "Patents & Technology Transfer"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bib", type=Path, default=Path("data/chang.bib"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    original = args.bib.read_text(encoding="utf-8")
    replacements: list[tuple[str, str]] = []
    for block in bib_entries(original):
        kind, key, fields = parse(block)
        if not is_paper(kind, fields) or "title" not in fields:
            continue
        old = fields["title"]
        # Legacy BibTeX sometimes wraps individual initial letters in braces
        # (for example {D}ynamic). Leave those hand-protected titles alone.
        if re.search(r"\{[A-Za-z]\}", old) or re.search(r"\}[A-Za-z]", old) or "�" in old:
            continue
        new = title_case(old)
        if new != old:
            replacements.append((old, new))
            print(f"{key}:\n  - {old}\n  + {new}")
    if args.write:
        updated = original
        for old, new in replacements:
            updated = updated.replace(f"title = {{{old}}}", f"title = {{{new}}}", 1)
        args.bib.write_text(updated, encoding="utf-8")
    print(f"{len(replacements)} title(s) {'updated' if args.write else 'need updating'}.")


if __name__ == "__main__":
    main()
