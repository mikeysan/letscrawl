# Refactor Plan: LetsCrawl as a Crawl4AI-Based Research Scraping Platform

## Purpose

This document proposes a way forward for `letscrawl` based on the most likely original intent of the project:

- build a lightweight scraping platform for research workflows
- scrape content from multiple sites using reusable configurations
- rely on Crawl4AI as the crawl and extraction engine
- produce structured outputs that can be exported and analyzed later

The immediate goal is not to add features quickly. The goal is to simplify the project around a clear architecture so future work is predictable.

## Working Hypothesis

The project appears to have started moving in two directions at once:

1. a Crawl4AI-based extraction platform
2. a custom async crawler with its own fetcher, rate limiting, URL utilities, and tests

The first direction aligns with the likely product goal. The second direction looks like infrastructure work that may have been started because:

- Crawl4AI alone did not yet express all of the control you wanted at the time
- you wanted explicit security controls such as SSRF blocking, robots checks, and rate limiting
- you were experimenting with lower-level crawling before settling on the product surface
- you wanted more confidence from unit tests than browser-driven extraction code typically gives

Those are reasonable motivations. The problem is that the repo now has two overlapping architectures, and they are not converging.

## Recommendation

Move the project fully toward this product definition:

> `letscrawl` is a config-driven research scraping platform built on Crawl4AI for collecting structured content from multiple websites and exporting it for downstream analysis.

That means:

- Crawl4AI becomes the only crawl and extraction engine
- the custom crawler path is removed, archived, or clearly separated as non-product code
- source configuration, extraction strategy selection, output normalization, and job execution become the main concerns

## Product Direction

The platform should support research collection jobs such as:

- multi-site news collection
- blog or publication monitoring
- structured article extraction across source lists
- feed discovery and content inventory
- site-specific extraction recipes for organizations, directories, or archives

It should not try to be a general-purpose crawler framework first. That is where scope expands and clarity disappears.

## Core Design Principles

1. Crawl4AI is the engine, not just a dependency.

Use Crawl4AI idiomatically:

- `AsyncWebCrawler`
- `BrowserConfig`
- `CrawlerRunConfig`
- Crawl4AI extraction strategies
- browser/session management only where needed

2. Configurations define jobs.

A job should answer:

- what sources to crawl
- how to identify content
- which extraction strategy to use
- what schema to return
- how to paginate or expand discovery
- how to export the results

3. Prefer deterministic extraction when possible.

Use CSS or schema-based extraction for stable repetitive pages. Use LLM extraction only when page structure is irregular or fields require semantic interpretation.

4. Normalize output for research.

Researchers care about consistency across sources. The platform should normalize:

- title
- source
- author
- publication date
- URL
- summary or content
- tags or categories
- retrieval timestamp
- crawl metadata

5. Keep source-specific logic declarative.

The more logic that lives in code instead of configuration, the harder it becomes to add and maintain new sources.

## Why Not Just Use Crawl4AI Directly?

A plain Crawl4AI script is useful for one-off extraction. This project still makes sense if it adds structure around Crawl4AI:

- source registry and job configs
- reusable schemas
- standardized exports
- multi-source orchestration
- post-processing and normalization
- testability around config behavior
- a cleaner CLI for research jobs

That is the value of `letscrawl`: not replacing Crawl4AI, but packaging it into a repeatable research workflow.

## Proposed Target Architecture

### 1. Job Layer

This is the user-facing layer.

Responsibilities:

- choose a job or source set
- load source definitions
- choose extraction strategy
- run the crawl
- save outputs and metadata

Possible structure:

```text
main.py
jobs/
  registry.py
  runner.py
  models.py
```

### 2. Source Config Layer

This defines what to crawl and how.

Responsibilities:

- source metadata
- start URLs
- allowed domains
- CSS selectors
- pagination rules
- extraction strategy type
- schema selection
- output mapping

Possible structure:

```text
sources/
  news/
    seneweb.py
    namibian.py
    newtimes.py
  rss/
    generic.py
  shared.py
```

Alternative:

- keep configs in Python for now
- later migrate selected source configs to YAML or TOML if needed

Python is fine initially because the source configs will likely need logic.

### 3. Extraction Layer

This adapts source config to Crawl4AI strategy objects.

Responsibilities:

- build `BrowserConfig`
- build `CrawlerRunConfig`
- choose CSS vs LLM extraction
- support per-source instructions
- support translation only as a post-processing concern unless there is a strong reason to keep it in extraction

Possible structure:

```text
extraction/
  strategies.py
  runner.py
  browser.py
```

### 4. Schema and Normalization Layer

This is where the current project needs the most discipline.

Responsibilities:

- define canonical research item models
- validate source output
- map source-specific fields into canonical fields
- attach metadata such as source name and crawl timestamp

Possible structure:

```text
models/
  canonical.py
  news.py
  feed.py
normalize/
  articles.py
  feeds.py
```

### 5. Output Layer

Responsibilities:

- CSV export
- JSON export
- line-delimited JSON export
- optional raw extraction snapshots for debugging

Possible structure:

```text
outputs/
  writers.py
  filenames.py
```

### 6. Tests

Responsibilities:

- config validation
- strategy selection
- normalization correctness
- CLI behavior
- mocked Crawl4AI result parsing

Avoid making browser-driven tests the only source of confidence.

## What To Do With the Existing Custom Crawler

### Recommendation

Deprecate it as product code.

Files affected:

- `crawler.py`
- `fetcher.py`
- `security.py`
- `url_utils.py`

These modules can be handled in one of three ways:

1. remove them entirely after replacement
2. move them into `legacy/` while refactoring
3. retain only narrowly useful utilities if they still apply cleanly

I recommend option 2 during the refactor, then option 1 later.

### Rationale

These modules solve lower-level problems than the current product needs. They also create the wrong center of gravity for the repo. The project should be organized around research jobs and source configs, not around maintaining a parallel crawler stack.

## Strategy Model

Each source should declare one of a small number of extraction modes.

### Mode A: CSS Structured Extraction

Use when:

- content cards or article lists have stable structure
- fields can be extracted with selectors
- speed and repeatability matter

Examples:

- article listings
- directory cards
- product grids
- feed links

### Mode B: LLM Structured Extraction

Use when:

- source markup is messy or inconsistent
- fields require semantic judgment
- content blocks vary too much for selectors alone

Examples:

- article body extraction across inconsistent templates
- summary generation
- fields like stance, topic, or named entities later on

### Mode C: Hybrid

Use when:

- CSS can identify candidate blocks or URLs
- LLM is used only for detailed extraction after narrowing the scope

This is likely the most useful long-term pattern for research crawling.

## Canonical Data Model

For the first refactor pass, I recommend one canonical model for article-like content:

```text
id
source_name
source_type
source_url
title
author
published_at
summary
content
language
tags
retrieved_at
raw_url
```

And one for feed discovery:

```text
source_name
site_url
feed_url
feed_valid
retrieved_at
```

The current schema is too loose and already drifted away from configs. The next version should be stricter, not looser.

## CLI Direction

The CLI should describe jobs clearly.

Suggested shape:

```bash
python main.py list-jobs
python main.py run news-africa
python main.py run news-africa --output json
python main.py run feed-discovery --urls https://cnn.com https://bbc.com
python main.py validate-config news-africa
```

This is better than a single `--config` flag carrying too much meaning.

## Refactor Phases

## Phase 1: Establish the New Product Shape

Goal:

- define the target architecture without changing behavior too aggressively

Tasks:

- add this plan to the repo
- choose a canonical directory layout
- define the canonical research item models
- define a source config contract
- decide which current configs are worth keeping

Deliverable:

- a clear module map and typed config model

## Phase 2: Repair the Current Main Path

Goal:

- make the existing Crawl4AI path internally consistent

Tasks:

- fix CLI issues such as `--list`
- reconcile config fields with the actual schema
- stop logging API key prefixes
- add validation so invalid configs fail early
- remove duplicate or stale README behavior

Deliverable:

- the current script becomes safe and coherent enough to refactor from

## Phase 3: Introduce Typed Source Definitions

Goal:

- move from free-form config dictionaries to typed source definitions

Tasks:

- create source config models using Pydantic
- define supported extraction modes
- define pagination and site-list models
- convert existing `news` and `rss` configs first

Deliverable:

- a typed source registry with two working source groups

## Phase 4: Separate Job Orchestration From Extraction

Goal:

- keep Crawl4AI usage isolated behind an execution layer

Tasks:

- move browser config creation out of utility sprawl
- move Crawl4AI run config creation into a focused module
- create a runner that accepts typed jobs and returns normalized results
- support CSS and LLM strategies through one interface

Deliverable:

- one orchestrator for all crawl jobs

## Phase 5: Add Normalization and Output Contracts

Goal:

- make results analyzable across sources

Tasks:

- normalize field names
- attach consistent metadata
- export CSV and JSON
- optionally save raw extracted payloads for debugging

Deliverable:

- predictable, research-ready outputs

## Phase 6: Add Real Tests for the Product Path

Goal:

- test the code users will actually run

Tasks:

- add tests for source config validation
- add tests for CLI command parsing
- add tests for strategy selection
- add tests for normalization
- mock Crawl4AI results instead of using live browser/network integration for most tests

Deliverable:

- stable and meaningful test coverage

## Phase 7: Remove or Archive Legacy Crawler Code

Goal:

- eliminate architectural ambiguity

Tasks:

- move `crawler.py`, `fetcher.py`, `security.py`, and `url_utils.py` into `legacy/`
- remove references from docs and tooling
- delete after confidence is high

Deliverable:

- one architecture, not two

## Recommended First Implementation Slice

The safest first slice is:

1. repair the current CLI and config/schema mismatch
2. create typed source models
3. migrate `news` and `rss` into the new structure
4. add normalization for article and feed outputs
5. add tests around those two job types

This slice keeps the project grounded in actual use cases you already cared about.

## Suggested Initial Scope

Start with two supported workflows only:

### Workflow 1: Multi-Site News Collection

Use case:

- collect articles from a curated list of news websites for research

Output:

- normalized article records

Why first:

- it matches your remembered intent
- you already have a partial implementation
- it exercises multi-source config, pagination, extraction, and normalization

### Workflow 2: Feed Discovery

Use case:

- find and validate RSS or Atom feeds for a list of sites

Output:

- feed inventory with validation status

Why second:

- lower complexity
- useful for research collection pipelines
- fits Crawl4AI plus simple post-processing well

## What Not To Do Yet

Do not add these before the platform shape is stable:

- a database
- background workers
- browser profile management
- scheduling
- UI/dashboard
- social platform connectors
- complex entity extraction or NLP pipelines

Those may make sense later, but not before the source/job/extraction contract is stable.

## Open Decisions

These should be resolved during implementation:

1. Should translation remain part of extraction, or move to optional post-processing?
2. Should source configs stay in Python, or eventually move to YAML?
3. Do we want one canonical schema for all content, or separate models by job type?
4. Should raw Crawl4AI output always be persisted for traceability?
5. Should legacy security utilities be preserved anywhere, or dropped fully?

My current recommendation:

- keep translation optional and move it out of core extraction later
- keep configs in Python for now
- use separate canonical models by job type
- save raw outputs only behind a debug flag
- archive legacy crawler code temporarily, then remove it

## Proposed End State

At the end of the refactor, `letscrawl` should feel like this:

- a researcher defines or selects a source job
- the job declares source URLs, extraction mode, schema, and output behavior
- Crawl4AI handles page loading and extraction
- `letscrawl` handles orchestration, normalization, validation, and export
- tests verify configuration and result handling without depending on live network behavior

That is a coherent product. The current repo is close enough to that idea that a refactor is justified, rather than a rewrite.

## Immediate Next Step

If this plan matches your intent, the next implementation step should be:

- Phase 2 plus the beginning of Phase 3

In practical terms:

- fix the current main path
- introduce typed source definitions
- migrate `news` and `rss` first

That gives us a stable base while staying close to the original idea of multi-site research scraping.
