# Legacy Crawler Code (Archived)

This directory contains the **legacy custom crawler implementation** that was
used before the project migrated to Crawl4AI-based extraction.

## Status: **DEPRECATED**

This code is **NOT USED** in the current application. It has been archived
for reference purposes only and will be deleted in a future update.

## Contents

- **crawler.py**: Async web crawler with queue-based BFS traversal
- **fetcher.py**: Async HTTP client with retry logic and security checks
- **security.py**: Security utilities (robots.txt compliance, rate limiting)
- **url_utils.py**: URL normalization and SSRF protection

## Why This Code Was Archived

The refactor (Phases 1-7, completed 2026-03-27) moved the project to a
Crawl4AI-based architecture:

- **Old**: Custom async crawler with separate infrastructure
- **New**: Crawl4AI-based extraction with typed configurations

## Migration Path

1. ✅ Extraction functionality replaced by `extraction/` package
2. ✅ Security utilities preserved (SSRF, robots.txt - can be extracted if needed)
3. ✅ Source configurations now typed via `models/source.py`
4. ✅ Job orchestration via `extraction/runner.py`

## Tests

The legacy code still has tests in `tests/test_crawler.py`,
`tests/test_fetcher.py`, `tests/test_security.py`, and
`tests/test_url_utils.py`. These tests continue to pass but test
archived code, not the production path.

## Future Actions

- [ ] Extract any useful security utilities (if needed for Crawl4AI path)
- [ ] Archive or delete legacy tests
- [ ] Delete this directory after confidence period (2+ weeks)

## Refactor Reference

See `REFACTOR_PLAN.md` and `MODULE_MAP.md` for details on the
refactoring process that led to this code being archived.
