# Building the paper

Requires pdflatex and bibtex (TeX Live / MacTeX).

    cd paper
    make          # main.pdf
    make check    # fails if body pages (before References) > 5, counts \todo markers
    make clean

Manual equivalent:

    pdflatex main && bibtex main && pdflatex main && pdflatex main

Style: `neurips_2026.sty` from the mandatory BrainBodyFM zip, loaded with
`[dblblindworkshop]` (anonymous). Add `final` after acceptance.
Placeholders: `\todo{...}` renders red inline; `\NUM` is a red `--` table cell.
