# make        : full pdflatex + bibtex + pdflatex x2
# make check  : fail if main body (before References) exceeds 4 pages
# make clean  : remove build artifacts
MAIN = main
PDFLATEX = pdflatex -interaction=nonstopmode -halt-on-error

.PHONY: all check clean

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex refs.bib neurips_2026.sty
	$(PDFLATEX) $(MAIN)
	bibtex $(MAIN)
	$(PDFLATEX) $(MAIN)
	$(PDFLATEX) $(MAIN)

# \label{lastbodypage} sits immediately before \bibliography in main.tex.
# The .aux records the page it landed on; body pages = that page number.
check: $(MAIN).pdf
	@body=$$(grep -o '\\newlabel{lastbodypage}{{[^}]*}{[0-9]*}' $(MAIN).aux | sed 's/.*}{\([0-9]*\)}$$/\1/'); \
	total=$$(pdfinfo $(MAIN).pdf | awk '/^Pages:/{print $$2}'); \
	echo "body pages: $$body (total incl. refs: $$total)"; \
	if [ -z "$$body" ]; then echo "check: lastbodypage label missing"; exit 1; fi; \
	if [ "$$body" -gt 4 ]; then echo "check: FAIL, body exceeds 4 pages"; exit 1; fi; \
	echo "check: OK"

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out $(MAIN).pdf
