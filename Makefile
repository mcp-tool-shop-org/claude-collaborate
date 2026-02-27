.PHONY: verify lint typecheck test

verify: lint typecheck test
	@echo "All checks passed"

lint:
	python -m ruff check .

typecheck:
	python -m mypy server.py ws_bridge.py

test:
	python -m pytest tests/
