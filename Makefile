PYTHON		= python3
MAIN		= a_maze_ing.py
CONFIG		= config.txt

.PHONY: install run debug clean lint lint-strict

install:
	uv venv
	uv pip install flake8 mypy

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	.venv/bin/flake8 .
	.venv/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	.venv/bin/flake8 .
	.venv/bin/mypy . --strict
