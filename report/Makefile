filename=report

#pdf: ps
#	ps2pdf ${filename}.ps
#
#ps: dvi
#	dvips ${filename}.dvi

pdf: ${filename}.tex
	pdflatex $^
	bibtex $(basename $^).aux || true
	pdflatex $^
	pdflatex $^

clean:
	rm -f $(addprefix ${filename}, .ps .pdf .log .aux .out .dvi .bbl .blg)
