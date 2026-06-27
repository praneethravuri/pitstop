# Contributing to Pitstop

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

```bash
git clone https://github.com/praneethravuri/pitstop.git
cd pitstop
uv sync --dev
git config core.hooksPath .githooks   # activate pre-commit hook
```

## Running Tests

```bash
uv run pytest tests/ -q
```

## Code Style

Ruff is enforced via the pre-commit hook on every commit:

```bash
uv run ruff format src/ tests/
uv run ruff check --fix src/ tests/
```

## Making Changes

1. Fork the repo and create a branch from `main`
2. Write tests before implementation (TDD)
3. Keep commits small and focused with a single-line message
4. Ensure `uv run pytest` and `uv run ruff check` pass before opening a PR
5. Open a PR against `main` — CI runs automatically

## Reporting Bugs

Open a GitHub issue with steps to reproduce, expected behaviour, and actual behaviour.

## Security Issues

See [SECURITY.md](SECURITY.md) for the vulnerability reporting process.
