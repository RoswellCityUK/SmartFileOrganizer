.PHONY: install test lint format clean

install:
	pip install --upgrade pip
	pip install -e .
	pip install pytest pytest-cov black mypy pre-commit

test:
	pytest

lint:
	mypy src
	pre-commit run --all-files

format:
	black src tests

clean:
	rm -rf build dist *.egg-info .pytest_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +