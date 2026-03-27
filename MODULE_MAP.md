# LetsCrawl Module Map

**Phase 1 Deliverable**: Canonical directory layout and module organization

## Current State (Pre-Refactor)

```
letscrawl/
├── main.py                 # CLI entry point, orchestration (338 lines)
├── config.py               # Configuration templates (290 lines)
├── crawler.py              # Legacy custom crawler (142 lines)
├── fetcher.py              # Legacy async fetcher (103 lines)
├── security.py             # Legacy security utilities (82 lines)
├── url_utils.py            # Legacy URL utilities (92 lines)
├── create_config.py        # Interactive config generator
├── my_configs.py           # User custom configs
├── models/
│   └── item.py             # Generic ScrapedItem model (30 lines)
└── utils/
    ├── scraper_utils.py    # Crawl4AI integration (377 lines)
    ├── data_utils.py       # CSV export (66 lines)
    └── logger.py           # Logging (55 lines)
```

## Target Architecture (Post-Refactor)

```
letscrawl/
├── main.py                 # CLI entry point (streamlined)
│
├── jobs/                   # Job orchestration layer (user-facing)
│   ├── __init__.py
│   ├── models.py           # Job definition models
│   ├── runner.py           # Job execution engine
│   └── registry.py         # Source registry
│
├── sources/                # Source configuration layer
│   ├── __init__.py
│   ├── news/               # News source configurations
│   │   ├── __init__.py
│   │   ├── seneweb.py
│   │   ├── namibian.py
│   │   └── newtimes.py
│   ├── rss/                # RSS feed configurations
│   │   ├── __init__.py
│   │   └── generic.py
│   └── shared.py           # Shared source utilities
│
├── extraction/             # Extraction strategy layer
│   ├── __init__.py
│   ├── strategies.py       # Strategy factory (CSS, LLM, Hybrid)
│   ├── browser.py          # Browser configuration
│   └── runner.py           # Crawl4AI execution wrapper
│
├── models/                 # Canonical data models
│   ├── __init__.py
│   ├── canonical.py        # Base ScrapedItem with metadata
│   ├── news.py             # Article model
│   ├── feed.py             # FeedDiscovery model
│   └── item.py             # Legacy generic model (keep for compatibility)
│
├── normalize/              # Normalization layer
│   ├── __init__.py
│   ├── articles.py         # Article field normalization
│   └── feeds.py            # Feed field normalization
│
├── outputs/                # Export and output layer
│   ├── __init__.py
│   ├── writers.py          # CSV, JSON export functions
│   └── filenames.py        # Output file naming
│
├── utils/                  # Utility modules (keep existing)
│   ├── __init__.py
│   ├── logger.py           # Centralized logging
│   └── data_utils.py       # Legacy data utilities (will refactor)
│
├── legacy/                 # Archived legacy code (Phase 7)
│   ├── crawler.py          # Custom async crawler (archived)
│   ├── fetcher.py          # Async fetcher (archived)
│   ├── security.py         # Security utilities (archived)
│   └── url_utils.py        # URL utilities (archived)
│
├── tests/                  # Test suite (expanded)
│   ├── conftest.py
│   ├── test_jobs/          # Job orchestration tests
│   ├── test_extraction/    # Extraction strategy tests
│   ├── test_normalize/     # Normalization tests
│   └── test_legacy/        # Legacy tests (keep for now)
│
└── Documentation/           # Documentation files
    ├── README.md
    ├── ARCHITECTURE.md
    ├── REFACTOR_PLAN.md
    ├── MODULE_MAP.md       # This file
    └── IMPROVEMENTS.md
```

## Layer Responsibilities

### 1. Jobs Layer (`jobs/`)

**Purpose**: User-facing job orchestration

**Responsibilities**:
- Accept job configurations (source sets, extraction mode, output format)
- Load source definitions from registry
- Coordinate extraction and normalization
- Handle errors and retry logic
- Export results and metadata

**Key Modules**:
- `models.py`: Pydantic models for job definitions
- `runner.py`: Main job execution engine
- `registry.py`: Source discovery and loading

### 2. Sources Layer (`sources/`)

**Purpose**: Source configuration and metadata

**Responsibilities**:
- Define source URLs, domains, and patterns
- Specify CSS selectors per source
- Define pagination rules
- Declare extraction strategy type
- Map fields to canonical schemas

**Key Modules**:
- `news/`: News source configurations
- `rss/`: RSS feed configurations
- `shared.py`: Shared source utilities

### 3. Extraction Layer (`extraction/`)

**Purpose**: Isolate Crawl4AI usage and strategy selection

**Responsibilities**:
- Build BrowserConfig objects
- Build CrawlerRunConfig objects
- Choose between CSS, LLM, or Hybrid strategies
- Execute crawls via Crawl4AI
- Return raw extracted data

**Key Modules**:
- `strategies.py`: Strategy factory and selection
- `browser.py`: Browser configuration
- `runner.py`: Crawl4AI execution wrapper

### 4. Models Layer (`models/`)

**Purpose**: Define canonical data schemas

**Responsibilities**:
- Define base ScrapedItem with metadata
- Define Article model for news/blogs
- Define FeedDiscovery model for RSS feeds
- Provide validation and serialization

**Key Modules**:
- `canonical.py`: Base model with metadata
- `news.py`: Article model
- `feed.py`: FeedDiscovery model

### 5. Normalization Layer (`normalize/`)

**Purpose**: Normalize extracted data to canonical schemas

**Responsibilities**:
- Map source-specific fields to canonical fields
- Attach metadata (source_name, retrieved_at, etc.)
- Validate against canonical schemas
- Handle missing or inconsistent fields

**Key Modules**:
- `articles.py`: Article normalization
- `feeds.py`: Feed normalization

### 6. Outputs Layer (`outputs/`)

**Purpose**: Export normalized results

**Responsibilities**:
- Write CSV exports
- Write JSON exports
- Generate output filenames
- Optional: Save raw output behind --debug flag

**Key Modules**:
- `writers.py`: CSV/JSON export functions
- `filenames.py`: Output naming conventions

## Migration Path

### Phase 1 (Current)
- ✅ Create `models/canonical.py`, `models/news.py`, `models/feed.py`
- ✅ Create this MODULE_MAP.md document
- ✅ Define source config contract (next step)

### Phase 2
- Repair CLI and config/schema mismatch
- Fix --list flag behavior
- Remove API key prefix logging

### Phase 3
- Create `jobs/models.py` with Pydantic source config models
- Migrate `news` and `rss` configs to typed definitions
- Create `sources/` directory structure

### Phase 4
- Create `extraction/` directory
- Isolate browser config creation
- Isolate Crawl4AI run config creation
- Create job runner

### Phase 5
- Create `normalize/` directory
- Implement field normalization
- Attach metadata
- Create `outputs/` directory

### Phase 6
- Add tests for all new modules
- Mock Crawl4AI results
- Achieve >80% coverage

### Phase 7
- Archive legacy code to `legacy/`
- Update documentation
- Delete after confidence period

## Design Principles

1. **Crawl4AI is the Engine**: All extraction goes through Crawl4AI
2. **Configurations Define Jobs**: What to crawl, how to extract, what to return
3. **Deterministic When Possible**: Prefer CSS extraction over LLM when feasible
4. **Normalize for Research**: Consistent fields across sources
5. **Declarative Sources**: Keep source logic in config, not code
6. **Isolate Crawl4AI**: Extraction layer abstracts Crawl4AI details
7. **Testable Without Browser**: Mock Crawl4AI for unit tests

## Success Criteria

- [ ] Module map document created ✅
- [ ] Canonical models defined (Article, FeedDiscovery) ✅
- [ ] Source config contract specified (next)
- [ ] Directory layout chosen (above)
- [ ] Decision made on which configs to keep (news, rss)

## Next Steps

1. Define source config contract using Pydantic models
2. Decide which current configs are worth keeping (news, rss confirmed)
3. Begin Phase 2: Repair Current Main Path
