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
	rm -rf build dist *.egg-info *.spec .pytest_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +

build:
	pip install pyinstaller
	pyinstaller --name smart-organizer \
		--onefile \
		--clean \
		--paths src \
		src/run.py
	@echo "Build complete. Binary is located at dist/smart-organizer"