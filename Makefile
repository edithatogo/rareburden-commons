PYTHON ?= python

.PHONY: install validate validate-catalog validate-roadmap test lint links safety compile check

install:
	$(PYTHON) -m pip install -e ".[dev]"

validate:
	PYTHONPATH=src $(PYTHON) -m rareburden validate-programme

validate-catalog:
	PYTHONPATH=src $(PYTHON) -m rareburden validate-catalog

validate-roadmap:
	PYTHONPATH=src $(PYTHON) -m rareburden validate-roadmap

test:
	PYTHONPATH=src $(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

links:
	PYTHONPATH=src $(PYTHON) scripts/check_markdown_links.py

safety:
	PYTHONPATH=src $(PYTHON) scripts/check_repository_safety.py

compile:
	$(PYTHON) -m compileall -q src scripts

check: validate test lint links safety compile
