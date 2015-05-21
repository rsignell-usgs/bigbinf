default:
	latexmk -pdf proposal.tex
clean:
	@rm -f *.aux *.fls *.log *.blg *.dvi *.bbl *.fdb_latexmk
watch:
	latexmk -pdf -pvc -silent proposal.tex
