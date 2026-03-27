# Legacy Tests (Deprecated)

This directory contains tests for the **deprecated custom crawler code**
that was archived during the Phase 7 refactor (March 2026).

## Status: **DEPRECATED - NOT PART OF PRODUCTION**

These tests verify functionality of the legacy custom crawler
(`crawler.py`, `fetcher.py`, `security.py`, `url_utils.py`) that is
**NOT USED** in the current LetsCrawl application.

## Current Application

The production LetsCrawl application now uses:
- **Crawl4AI** for web crawling and extraction
- **Typed source configurations** (`models/source.py`)
- **Extraction layer** (`extraction/` package)
- **Canonical data models** (`models/canonical.py`, `models/news.py`)

## Why Keep These Tests?

These tests are preserved for:
1. **Reference**: Security patterns (SSRF protection, robots.txt, rate limiting)
2. **Documentation**: Examples of how the legacy system worked
3. **History**: Understanding the refactor decisions

## Running These Tests

To run these legacy tests:

```bash
# From the repository root
python -m pytest legacy/tests/ -v
```

**Note**: These tests are **NOT** part of the main test suite and will
**NOT** be run by CI/CD pipelines. They test archived functionality only.

## Test Files

- **test_crawler.py**: Tests the legacy WebCrawler class
- **test_fetcher.py**: Tests the legacy AsyncFetcher with retry logic
- **test_security.py**: Tests security utilities (RateLimiter, RobotsTxtChecker)
- **test_url_utils.py**: Tests URL utilities (SSRF protection, normalization)

## Migration Path

The current production code has **NO tests** yet. See Phase 6 of the
refactor plan for adding tests for:
- Config validation
- Extraction layer
- Normalization functions
- CLI commands

## Future Actions

When production test coverage is added (Phase 6):
- These legacy tests can be moved to `tests/legacy/` (if still needed)
- Or deleted entirely once the security patterns are extracted
- CI/CD should run `tests/` (production tests) not `legacy/tests/` (deprecated tests)

---

**Refactor Reference**: See `REFACTOR_PLAN.md` and `MODULE_MAP.md` for details on
the refactoring that archived this code.
