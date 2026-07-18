PYTHON ?= python

.PHONY: install validate test lint safety check

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

validate:
	PYTHONPATH=src $(PYTHON) -m rareburden validate-catalog

test:
	PYTHONPATH=src $(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

safety:
	PYTHONPATH=src $(PYTHON) scripts/check_repository_safety.py

check: validate test safety
	$(PYTHON) -m compileall -q src
