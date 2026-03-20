.PHONY: help install lint type-check test test-all check clean

help:           ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:        ## Install dependencies using uv
	uv pip install -r requirements.txt

lint:           ## Run ruff linter
	uv run ruff check .

type-check:     ## Run mypy type checker
	uv run mypy .

test:           ## Run pytest with coverage (exclude integration tests)
	uv run pytest tests/ --ignore=tests/test_crawler.py -v --tb=short --cov=.

test-all:       ## Run all tests including integration tests
	uv run pytest tests/ -v --tb=short --cov=.

check:          ## Run all checks (lint + type-check + test)
check: lint type-check test

clean:          ## Clean up generated files
	rm -rf .venv/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
