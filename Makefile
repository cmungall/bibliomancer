RUN = poetry run
CODE = src/bibliomancer
DM = $(CODE)/datamodel

all: datamodel test trigger integration-test

datamodel: $(DM)/biblio.py

test: pytest doctest


pytest:
	$(RUN) pytest

apidoc:
	$(RUN) sphinx-apidoc -f -M -o docs/ src/curate_gpt/ && cd docs && $(RUN) make html

doctest:
	$(RUN) python -m doctest --option ELLIPSIS --option NORMALIZE_WHITESPACE $(CODE)/*.py

%-doctest: %
	$(RUN) python -m doctest --option ELLIPSIS --option NORMALIZE_WHITESPACE $<


$(DM)/%.py: $(DM)/%.yaml
	$(RUN) gen-pydantic --pydantic-version 2 $< > $@.tmp && mv $@.tmp $@


trigger:
	touch tests/input/cjm.paperpile.csv
integration-test: tests/output/cjm.html

tests/output/%.json: tests/input/%.paperpile.csv
	$(RUN) bibliomancer export --repair -a "Mungall CJ?" --annotate-position -i $< -O json -o $@
.PRECIOUS: tests/output/%.json

tests/output/%-merged.json: tests/output/%.json tests/input/cjm.roles.csv
	$(RUN) bibliomancer merge -i $< -f json -s bibm -m tests/input/cjm.roles.csv -c role -O json -o $@
.PRECIOUS: tests/output/%-merged.json


tests/output/%.md: tests/output/%-merged.json $(CODE)/templates/default.markdown.jinja2
	$(RUN) bibliomancer export -f json -s bibm  --repair -a "Mungall CJ?" --annotate-position -i $< -O markdown -o $@

tests/output/%.html: tests/output/%.md
	pandoc $< -o $@

#src/bibliomancer/datamodel/z2cls-typeMap.xml: https://aurimasv.github.io/z2csl/typeMap.xml
#	curl -L -s $< > $@
