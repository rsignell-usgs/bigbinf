default:
	latexmk -pdf proposal.tex
proposal:
	latexmk -pdf proposal.tex
background:
	latexmk -pdf background_protocol.tex
	latexmk -pdf background_microcloud.tex
design:
	latexmk -pdf design_protocol.tex
	# latexmk -pdf design_microcloud.tex
clean:
	@rm -f *.aux *.fls *.log *.blg *.dvi *.bbl *.fdb_latexmk *.out
watch:
	latexmk -pdf -pvc -silent design_protocol.tex
