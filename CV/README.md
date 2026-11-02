# Ming-Ching Chang Curriculum Vitae

This is a standard LaTeX conversion of the current Word CV. The publication
sections are generated from `chang.bib`; other CV sections are maintained in
`cv_before_publications.tex` and `cv_after_publications.tex`.

## Update publications

1. Edit `chang.bib`.
2. Run `python build_cv.py`.
3. Compile `main.tex` (for example with `latexmk -pdf main.tex`).

The generator formats venues in italics, uses initials for authors, and
underlines Ming-Ching Chang in publication entries.
