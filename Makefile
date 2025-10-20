# Pitstop F1 MCP Server - Makefile

.PHONY: help install test lint format clean run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv sync

test: ## Run all tool tests
	uv run python test_runner.py

test-fast: ## Run tests excluding slow ones
	uv run pytest -m "not slow"

test-integration: ## Run integration tests only
	uv run pytest -m integration

lint: ## Run code quality checks
	uv run ruff check .

format: ## Format code with ruff
	uv run ruff format .

type-check: ## Run type checking with mypy
	uv run mypy server.py tools/ --ignore-missing-imports

clean: ## Clean cache and temporary files
	rm -rf cache/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf */*/__pycache__/
	rm -rf *.egg-info/
	rm -f test_results.json
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

cache-clean: ## Clean FastF1 cache only
	rm -rf cache/

run: ## Run the MCP server
	uv run mcp run server.py

dev: ## Install development dependencies
	uv sync --all-extras

check: lint type-check test ## Run all checks (lint, type-check, test)

ci: ## Run CI pipeline locally
	@echo "Running CI checks..."
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) test
	@echo "✓ All CI checks passed!"

.DEFAULT_GOAL := help
