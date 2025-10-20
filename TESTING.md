# Testing Guide

## Overview

Pitstop includes comprehensive automated testing for all 24 MCP tools.

---

## Quick Start

### Run All Tests

```bash
# Using test runner
python test_runner.py

# Using make
make test

# Using CI locally
make ci
```

### Run Specific Tests

```bash
# Test a single tool
python tools/session/results.py

# Test control tools
python tools/control/messages.py

# Test live timing
python tools/live/radio.py
```

---

## CI/CD Workflows

### 1. Test Workflow (`.github/workflows/test.yml`)

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main`
- Daily at 9 AM UTC (catches API/data issues)
- Manual trigger

**Tests:**
- ✅ Cross-platform (Ubuntu, Windows, macOS)
- ✅ Multi-Python (3.11, 3.12, 3.13)
- ✅ All 24 tools
- ✅ Code quality (linting, type checking)
- ✅ Integration tests

**Artifacts:**
- Test results JSON (30-day retention)

### 2. Release Workflow (`.github/workflows/release.yml`)

**Triggers:**
- Git tags matching `v*.*.*` (e.g., `v1.0.0`)
- Manual trigger

**Actions:**
- Runs full test suite
- Generates changelog from commits
- Creates GitHub release with notes

### 3. Cache Cleanup (`.github/workflows/cache-cleanup.yml`)

**Triggers:**
- Weekly on Sundays at midnight
- Manual trigger

**Actions:**
- Removes FastF1 cache files older than 30 days
- Reports cache size before/after

---

## Test Runner (`test_runner.py`)

Automated test suite that:
1. Discovers all tool files in `tools/`
2. Executes each tool's `if __name__ == "__main__"` test block
3. Reports pass/fail/skip status
4. Generates `test_results.json`

**Output:**
```
PITSTOP F1 MCP SERVER - TOOL TEST SUITE
========================================

Discovered 39 tool files

Testing: results
✓ results - PASSED

Testing: standings
✓ standings - PASSED

...

TEST SUMMARY
============
Total:   39
Passed:  24 ✓
Failed:  0 ✗
Skipped: 15 -
```

---

## Makefile Commands

```bash
# Development
make help          # Show all commands
make install       # Install dependencies
make dev           # Install with dev extras

# Testing
make test          # Run all tests
make test-fast     # Skip slow tests
make test-integration  # Integration tests only

# Code Quality
make lint          # Run ruff checks
make format        # Format code
make type-check    # Run mypy
make check         # Run all quality checks

# Maintenance
make clean         # Remove cache and temp files
make cache-clean   # Clear FastF1 cache only

# CI
make ci            # Run full CI pipeline locally
```

---

## Test Structure

### Tool Tests

Each tool file includes a test block:

```python
if __name__ == "__main__":
    # Test with real data
    print("Testing get_session_results...")
    results = get_session_results(2024, "Monaco", "R")
    print(f"Winner: {results.results[0].broadcast_name}")
```

### Test Types

**Unit Tests:**
- Individual tool functionality
- Parameter validation
- Data model serialization

**Integration Tests:**
- Server initialization
- Tool registration
- Cross-tool compatibility

**Smoke Tests:**
- Daily scheduled runs
- Catch API changes
- Validate data availability

---

## Local Testing

### Before Committing

```bash
# Run complete test suite
make ci

# Or step by step
make lint
make type-check
make test
```

### Test Specific Category

```bash
# Session tools
python tools/session/results.py
python tools/session/laps.py
python tools/session/standings.py

# Live timing
python tools/live/radio.py
python tools/live/pit_stops.py

# Analysis
python tools/historical/analysis.py
```

---

## Troubleshooting

### Test Failures

**FastF1 data not available:**
- Check internet connection
- Try different year/GP
- Clear cache: `make cache-clean`

**Import errors:**
- Reinstall: `make install`
- Check Python version: `python --version`

**Timeout errors:**
- Increase timeout in workflow
- Check data source availability

### Common Issues

**Issue:** "No module named 'fastf1'"
**Fix:** Run `uv sync`

**Issue:** Cache too large
**Fix:** Run `make cache-clean`

**Issue:** Test hangs
**Fix:** Ctrl+C and check network/API status

---

## Writing New Tests

### Tool Test Template

```python
if __name__ == "__main__":
    # Test basic functionality
    print("Testing new_tool...")

    try:
        result = new_tool(2024, "Monaco")
        assert result is not None
        assert len(result.data) > 0
        print(f"✓ Test passed: {len(result.data)} items")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise
```

### Best Practices

1. ✅ Use recent, stable data (2024 Monaco, Silverstone, etc.)
2. ✅ Test edge cases (missing data, invalid parameters)
3. ✅ Keep tests fast (<30 seconds per tool)
4. ✅ Print clear success/failure messages
5. ✅ Use assertions to validate output

---

## CI/CD Best Practices

### Before Merging PR

1. All tests passing ✓
2. No linting errors ✓
3. Type checks passing ✓
4. Test coverage maintained ✓

### Release Checklist

1. Update version in relevant files
2. Run full test suite: `make ci`
3. Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions creates release automatically

---

## Continuous Monitoring

### Daily Tests
- Scheduled workflow runs daily
- Catches F1 data source changes
- Validates API availability
- Email notifications on failure

### Cache Management
- Weekly automatic cleanup
- Prevents disk space issues
- Maintains performance

---

## Performance Metrics

**Average Test Times:**
- Single tool: ~5-10 seconds
- Full suite: ~5-10 minutes
- Integration tests: ~30 seconds

**Resource Usage:**
- Disk: ~500MB (FastF1 cache)
- Memory: ~200MB per test
- Network: ~10-50MB per tool

---

## Support

**Issues:**
- GitHub Issues: Report test failures
- Discussions: Ask questions

**Logs:**
- CI logs: Available in GitHub Actions
- Local logs: `test_results.json`

---

**Happy Testing! 🏎️**
