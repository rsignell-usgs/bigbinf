default:
	latexmk -pdf proposal.tex
proposal:
	latexmk -pdf proposal.tex
background:
	latexmk -pdf background_protocol.tex
	# latexmk -pdf background_cloud.tex
clean:
	@rm -f *.aux *.fls *.log *.blg *.dvi *.bbl *.fdb_latexmk
watch:
	latexmk -pdf -pvc -silent proposal.tex
