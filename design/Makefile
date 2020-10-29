TARGET=L3-T-2_Design

FIGURES_SRC=$(wildcard uml/*.uml)
FIGURES=$(patsubst uml/%.uml,uml/%.png,$(FIGURES_SRC))

# $(TARGET).pdf is phony so that we always call latexmk
.PHONY: $(TARGET).pdf all clean

all: $(TARGET).pdf

$(TARGET).pdf: $(TARGET).tex $(FIGURES)
	latexmk -pdf --bibtex -pdflatex="pdflatex -shell-escape -interaction=nonstopmode" -use-make $<

%.png : %.uml
	plantuml -tpng $<

clean:
	latexmk -bibtex -C
	rm $(FIGURES)

