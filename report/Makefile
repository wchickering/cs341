filename=report

pdf: ps
	ps2pdf ${filename}.ps

ps: dvi
	dvips ${filename}.dvi

dvi: ${filename}.tex
	latex $^
	bibtex $(basename $^).aux || true
	latex $^
	latex $^

clean:
	rm -f $(addprefix ${filename}, .ps .pdf .log .aux .out .dvi .bbl .blg)
