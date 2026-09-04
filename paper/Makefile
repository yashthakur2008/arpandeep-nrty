# Build: make. Page check: make check (fails if body pages > 5).
TEX = main
LIMIT = 5

all: $(TEX).pdf

$(TEX).pdf: $(TEX).tex refs.bib neurips_2026.sty
	pdflatex -interaction=nonstopmode -halt-on-error $(TEX) >/dev/null
	bibtex $(TEX) | grep -iE 'warning|error' || true
	pdflatex -interaction=nonstopmode -halt-on-error $(TEX) >/dev/null
	pdflatex -interaction=nonstopmode -halt-on-error $(TEX) | grep -E 'Output written|Warning: (Citation|Reference)' || true

check: $(TEX).pdf
	@body=$$(sed -n 's/.*newlabel{end:body}{{[^}]*}{\([0-9]*\)}.*/\1/p' $(TEX).aux); \
	echo "body pages: $$body (limit $(LIMIT))"; \
	test "$$body" -le $(LIMIT) || { echo "FAIL: body exceeds $(LIMIT) pages"; exit 1; }
	@n=$$(grep -c '\\todo' $(TEX).tex); echo "todo markers in source: $$n"

clean:
	rm -f $(TEX).{aux,bbl,blg,log,out,pdf}

.PHONY: all check clean
