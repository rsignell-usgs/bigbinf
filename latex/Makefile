default:
	make protocols
	make cloud
protocols:
	latexmk -pdf protocols.tex
cloud:
	latexmk -pdf microcloud.tex
clean:
	@rm -f *.aux *.fls *.log *.blg *.dvi *.bbl *.fdb_latexmk *.out
watch:
	latexmk -pdf -pvc -silent paper_protocols.tex
	# latexmk -pdf -pvc -silent paper_microcloud.tex
coversheet:
	gs -o thesis.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress PaperCoverSheet.pdf microcloud.pdf
