

# Refactoring Plan: letscrawl (Security & Architecture)

**Objective:** Refactor `letscrawl` to be secure, robust, and asynchronous.
**Constraint:**
1.  **Atomic Steps:** Every step must result in a passing test suite.
2.  **The Golden Rule:** If a test fails after implementation, **DO NOT** modify the test. Modify the *code implementation* until the test passes. Tests define the contract; code fulfills it.
3.  **Continuous Integration:** Run `pytest` after every code modification step.

---

## Phase 1: Project Hygiene & Dependencies
*Goal: Set up the environment for robust testing and async development.*

### Step 1.1: Dependency Definition
1.  Create a `requirements.txt` file (or `pyproject.toml`) with the following specific versions:
    *   `aiohttp>=3.9.0` (For Async HTTP)
    *   `beautifulsoup4>=4.12.0` (For Parsing)
    *   `pytest>=7.4.0` (For Testing)
    *   `pytest-asyncio>=0.21.0` (For Async testing support)
    *   `tenacity>=8.2.0` (For Retry logic)
2.  **Test:** Run `pip install -r requirements.txt`. Ensure no errors occur.

### Step 1.2: Test Framework Initialization
1.  Create a `tests/` directory in the project root.
2.  Create an empty `__init__.py` inside `tests/`.
3.  Create a `conftest.py` in `tests/` to configure `pytest-asyncio` (add `pytest_plugins = ('pytest_asyncio',)`).
4.  **Test:** Run `pytest` from the root directory. It should find 0 tests but exit successfully.

---

## Phase 2: URL Utilities (Security & Architecture Foundation)
*Goal: Prepare robust URL handling before fetching logic. Addresses SSRF and Deduplication.*

### Step 2.1: Create URL Normalizer
1.  Create a module `url_utils.py`.
2.  Define a function `normalize_url(url: str, base_url: str) -> str`.
3.  **Test (Write First):** In `tests/test_url_utils.py`:
    *   Test that relative URLs `/about` resolve to `base_url/about`.
    *   Test that fragments `#section` are removed.
    *   Test that scheme and domain are forced to lowercase.
4.  **Implementation:** Write the function to pass the tests using `urllib.parse`.

### Step 2.2: Implement SSRF Protection
1.  Add a function `is_safe_url(url: str) -> bool` in `url_utils.py`.
2.  **Test (Write First):**
    *   Test that `http://localhost:8000` returns `False`.
    *   Test that `http://127.0.0.1` returns `False`.
    *   Test that `http://169.254.169.254` (AWS metadata) returns `False`.
    *   Test that valid public IPs/domains return `True`.
3.  **Implementation:** Parse the hostname and check against private IP ranges (using `ipaddress` module) or blocklist keywords (`localhost`).

---

## Phase 3: Security & Ethical Standards
*Goal: Implement robots.txt compliance and Rate Limiting.*

### Step 3.1: Robots.txt Checker
1.  Create a module `security.py`.
2.  Define a class `RobotsTxtChecker`.
3.  **Test (Write First):**
    *   Mock `urllib.robotparser.RobotFileParser`.
    *   Test that `can_fetch(user_agent, url)` returns correct boolean based on mocked robots content.
4.  **Implementation:** Wrap `RobotFileParser`. Ensure it fetches and parses `robots.txt` for a given domain.

### Step 3.2: Rate Limiter
1.  Create a class `RateLimiter` in `security.py`.
2.  It should limit requests to a specific delay (e.g., 1 request per second).
3.  **Test (Write First):**
    *   Use `pytest-asyncio` to call the limiter twice rapidly.
    *   Assert that the second call takes at least $X$ seconds.
4.  **Implementation:** Use `asyncio.Lock` and track the last fetch time.

---

## Phase 4: Architecture Shift to Async I/O
*Goal: Replace synchronous `requests` with asynchronous `aiohttp`.*

### Step 4.1: Async Fetcher Skeleton
1.  Create a module `fetcher.py`.
2.  Create a class `AsyncFetcher` with an `__init__` taking `RateLimiter` and `RobotsTxtChecker`.
3.  **Test (Write First):** Instantiate the class. Assert attributes are set correctly.

### Step 4.2: Implement Async GET
1.  Add an `async def fetch(self, url: str) -> str` method.
2.  **Test (Write First):**
    *   Mock `aiohttp.ClientSession`.
    *   Mock the response to return `"<html>...</html>"`.
    *   Assert the method returns the correct text.
3.  **Implementation:** Use `aiohttp.ClientSession` context manager. Connect the mock.

### Step 4.3: Integrate Security & Error Handling in Fetch
1.  Update `fetch` to call `RobotsTxtChecker` before the request. Raise exception if disallowed.
2.  Update `fetch` to call `RateLimiter` before the request.
3.  Update `fetch` to handle `aiohttp.ClientError` gracefully (catch and log, or return None).
4.  **Test (Write First):**
    *   Test that a disallowed URL raises a `PermissionError` (or custom exception).
    *   Test that network errors return `None` (or raise a specific wrapper exception).
5.  **Implementation:** Wrap the fetching logic in `try/except` blocks.

---

## Phase 5: Robustness & Retry Logic
*Goal: Make the crawler resilient to transient failures.*

### Step 5.1: Implement Retry Logic
1.  Add the `@retry` decorator (from `tenacity`) to the `fetch` method in `fetcher.py`.
2.  Configure it to stop after 3 attempts and wait 1 second between retries.
3.  **Test (Write First):**
    *   Mock `aiohttp` to raise a `ServerDisconnectedError` twice, then succeed on the 3rd try.
    *   Assert that the method eventually returns the result.
    *   Mock `aiohttp` to raise error 4 times.
    *   Assert that the method raises the `RetryError` eventually.
4.  **Implementation:** Apply the decorator. If the test fails, adjust the *decorator parameters*, not the test.

---

## Phase 6: Main Orchestration
*Goal: Wire everything together in the main execution loop.*

### Step 6.1: Main Queue Loop
1.  Refactor the main execution block (or `main.py`) to use `asyncio.run()`.
2.  Use a `set` for visited URLs (enforcing normalization).
3.  Use a `collections.deque` or `asyncio.Queue` for the frontier.
4.  **Test (Write First):**
    *   Integration test: Spin up a local test server (using `aiohttp` test server or `pytest-httpserver`).
    *   Serve a page with one link.
    *   Run the crawler.
    *   Assert that 2 pages were fetched (root + link).
5.  **Implementation:** Orchestrate the loop:
    *   Pop URL from Queue.
    *   Check if visited.
    *   Fetch URL (using `AsyncFetcher`).
    *   Parse links (using `BeautifulSoup`).
    *   Normalize and Enqueue new links.

### Step 6.2: Final Integration Verification
1.  **Test:** Run `pytest --cov=.` (if coverage installed) to ensure code coverage is > 80%.
2.  **Verification:** Run the crawler manually against a public test site (e.g., `toscrape.com`). Observe logs. Ensure it respects delay and doesn't crash on 404s.
3.  **Final Rule Check:** Ensure no tests were modified in Step 6 to make them pass. If integration tests failed, fix the orchestration logic.

---

**Status:** You should proceed step-by-step. **Do not skip steps.** If Step 4.2 fails, do not move to 4.3.