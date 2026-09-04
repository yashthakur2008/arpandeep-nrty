# Build

Requires pdflatex, bibtex (TeX Live) and pdfinfo (poppler).

    make          # pdflatex, bibtex, pdflatex, pdflatex -> main.pdf
    make check    # fails if the body (before References) exceeds 4 pages
    make clean

Style: `neurips_2026.sty` (official 2026 file, ProvidesPackage 2026-01-29), loaded with
`[dblblindworkshop]` so the author block stays anonymous and the foot line names the
workshop. media.neurips.cc returned 404/403 for the 2026/2025/2024 style URLs on
2026-09-04; the copy came from the sibling worktree `loki-sleep-paper/paper/`.

Last local build (2026-09-04): compiled clean, 0 bibtex warnings, 0 undefined
citations, body = 4 pages, total = 7 pages with references.
