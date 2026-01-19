This plan assumes the codebase has been refactored into modules (`url_utils`, `security`, `fetcher`, etc.) and tests are already in place.

***

# Refactoring Plan: letscrawl (Quality, Docs, & CI/CD)

**Objective:** Enforce strict code quality standards, implement type safety, professionalize logging, and automate quality checks via CI/CD.
**Constraint:**
1.  **Atomic Steps:** Every step must result in a passing test suite or linting check.
2.  **The Golden Rule:** If a test (or linter) fails, **DO NOT** modify the test/linter config. Modify the *code implementation* until it passes. Linters define the style; code adheres to it.
3.  **Continuous Integration:** Run the specified checks after every code modification step.

---

## Phase 1: Code Quality & Static Analysis
*Goal: Enforce industry-standard style and catch type errors before runtime.*

### Step 1.1: Linter Setup (Ruff/Flake8)
1.  Add `ruff` to `requirements.txt` (or `dev-requirements.txt`). *Ruff is preferred for speed and modern Python standards.*
2.  Create a configuration file `ruff.toml` (or `.ruff.toml`) in the root.
    *   Set `line-length = 88` (standard).
    *   Enable select rules (e.g., `E`, `F`, `I` for Import sorting).
3.  **Test:** Run `ruff check .`.
    *   **Outcome:** The command executes (it may report errors, that is expected).
    *   **Pass Criteria:** The tool runs successfully.

### Step 1.2: Fix Linting Errors
1.  Run `ruff check --fix .` to auto-fix import sorting and simple whitespace issues.
2.  Manually fix any remaining errors reported by `ruff check .` (e.g., unused imports, variable naming).
3.  **Test:** Run `ruff check .`.
    *   **Pass Criteria:** The command returns Exit Code 0 (No errors found).

### Step 1.3: Type Checking Setup (Mypy)
1.  Add `mypy` to requirements.
2.  Create a `mypy.ini` (or `pyproject.toml` section) configuration:
    *   `strict = True` (or start with `check_untyped_defs = True`).
3.  **Test:** Run `mypy .`.
    *   **Outcome:** The command executes (may report missing types).

### Step 1.4: Add Type Hints to Core Modules
1.  Start with `url_utils.py`. Add function signatures (`-> str`, `-> bool`) and variable types.
2.  **Test:** Run `mypy url_utils.py`.
    *   **Pass Criteria:** No type errors reported for `url_utils.py`.
3.  Repeat for `security.py` and `fetcher.py`.
    *   **Test:** Run `mypy .` after each file.
    *   **Pass Criteria:** No type errors for the specific file being worked on.
4.  **Final Test:** Run `mypy .` on the whole project.
    *   **Pass Criteria:** Exit Code 0.

---

## Phase 2: Logging & Maintainability
*Goal: Replace debug prints with a structured logging system.*

### Step 2.1: Configure Logging Module
1.  Create a `logger.py` module (or add to a generic `utils.py`).
2.  Set up a basic configuration using `logging.basicConfig` (or `dictConfig`).
    *   Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
    *   Level: Allow configuration via environment variable (e.g., `LOG_LEVEL`).
3.  **Test:** Write a test in `tests/test_logger.py` that instantiates the logger and asserts that the handler is attached.
4.  **Implementation:** Write the config code.

### Step 2.2: Replace `print` with `logger` (Crawler Logic)
1.  Locate all `print()` statements in the main execution files.
2.  Replace them with `logger.info()`, `logger.warning()`, or `logger.error()` as appropriate.
3.  **Test:** Run the crawler integration tests.
    *   **Pass Criteria:** Tests pass (asserting on output) AND no `print` statements exist in the main python files (checked via `grep`).

### Step 2.3: Modularize Configuration
1.  Create a `config.py` file to hold constants (e.g., `DEFAULT_USER_AGENT`, `DEFAULT_DELAY`, `MAX_RETRIES`).
2.  Move hardcoded values from `fetcher.py` and `main.py` to `config.py`.
3.  **Test:** Write a test `tests/test_config.py` asserting that these constants exist and have expected types.
4.  **Implementation:** Move the constants.

---

## Phase 3: Documentation Standards
*Goal: Ensure code is self-documenting via Docstrings.*

### Step 3.1: Docstring Enforcer Setup
1.  Add `pydocstyle` to requirements.
2.  Create `.pydocstyle` config (convention: `pep257` or `google`).
3.  **Test:** Run `pydocstyle .`.
    *   **Outcome:** Command executes (reports missing docstrings).

### Step 3.2: Document Public APIs
1.  Add Google-style or NumPy-style docstrings to all public methods in `url_utils.py`, `security.py`, and `fetcher.py`.
    *   Include: Description, Args, Returns, Raises.
2.  **Test:** Run `pydocstyle .` on the specific file.
    *   **Pass Criteria:** No style errors for that file.
3.  Repeat for all modules.
4.  **Final Test:** Run `pydocstyle .`.
    *   **Pass Criteria:** Exit Code 0.

### Step 3.3: Update README
1.  Update `README.md` to reflect the new architecture.
    *   Sections: Installation (new requirements), Usage (CLI flags), Architecture diagram/text.
    *   Include badges for CI/CD (placeholders for now).
2.  **Test:** Verify that markdown renders correctly by viewing it in a markdown previewer or using a markdown linter (e.g., `markdownlint`).

---

## Phase 4: CI/CD Pipeline (GitHub Actions)
*Goal: Automate the quality checks defined in previous phases.*

### Step 4.1: Workflow Directory Structure
1.  Create directory path `.github/workflows/`.
2.  Create file `ci.yml`.
3.  **Test:** Verify file path exists.

### Step 4.2: Define Linting Job
1.  In `.github/workflows/ci.yml`, define a job `lint` that runs on `ubuntu-latest`.
2.  Steps: Checkout code, Install Python, Install requirements, Run `ruff check .`.
3.  **Test:** Install `act` (tool for running GitHub Actions locally) OR simply verify the YAML syntax is correct.
    *   **Verification:** Run `yamllint .github/workflows/ci.yml` (if available) or ensure the YAML is indented correctly.

### Step 4.3: Define Type Check Job
1.  Add job `type-check` to `ci.yml`.
2.  Steps: Install dependencies, Run `mypy .`.
3.  **Test:** Verify YAML syntax.

### Step 4.4: Define Test Job
1.  Add job `test` to `ci.yml`.
2.  Steps: Install dependencies, Run `pytest --cov=.`.
3.  **Test:** Verify YAML syntax.

### Step 4.5: Integration Verification
1.  **Simulation:** Run the exact commands defined in the YAML file locally in a clean virtual environment.
    *   Command sequence: `pip install -r requirements.txt` -> `ruff check .` -> `mypy .` -> `pytest`.
2.  **Pass Criteria:** All commands run successfully and exit with code 0 locally.
3.  **Action:** Commit and push the `.github/workflows/ci.yml` file to the repository.
    *   **Final Check:** Monitor the GitHub Actions tab on the repository to ensure the pipeline passes green.

---

**Status:** You should proceed step-by-step. **Do not skip steps.** If `pydocstyle` complains about a docstring format, rewrite the docstring, do not disable the linter.