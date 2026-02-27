# capiscio-python - GitHub Copilot Instructions

## ABSOLUTE RULES - NO EXCEPTIONS

### 1. ALL WORK VIA PULL REQUESTS
- **NEVER commit directly to `main`.** All changes MUST go through PRs.

### 2. LOCAL CI VALIDATION BEFORE PUSH
- Run: `pytest -v`

### 3. NO WATCH/BLOCKING COMMANDS
- **NEVER run blocking commands** without timeout

---

## CRITICAL: Read First

**If working inside the CapiscIO monorepo workspace that includes `.context/`, read these workspace context files before starting work:**
1. `../../.context/CURRENT_SPRINT.md` - Sprint goals and priorities
2. `../../.context/ACTIVE_TASKS.md` - Active tasks

If these files are not present in your checkout of this repository, skip this step.

---

## Repository Purpose

**capiscio-python** is the Python/PyPI CLI wrapper for capiscio-core. It auto-downloads
the platform-specific Go binary and passes all commands through transparently.

Published to PyPI as `capiscio`. Users install via `pip install capiscio`.

**This is NOT the Python SDK** — that's `capiscio-sdk-python`.

**Technology Stack**: Python 3.10+, hatchling (build), rich (CLI output)

**Current Version**: v2.4.0 (wrapper); core binary version is controlled by `CORE_VERSION` in `src/capiscio/manager.py`
**Default Branch:** `main`

## Architecture

This is a **thin passthrough wrapper**, NOT a reimplementation. All logic lives in capiscio-core.

```
capiscio-python/
├── src/capiscio/
│   ├── __init__.py
│   ├── cli.py               # Main entry point - parses args, delegates to binary
│   └── manager.py           # Downloads + caches platform-specific capiscio-core binary
├── tests/                   # Test suite
├── pyproject.toml           # Package config (name: "capiscio", hatchling build)
└── docs/                    # Documentation
```

### How It Works

1. User runs `capiscio validate agent-card.json`
2. `cli.py` invokes `manager.run_core()` to ensure Go binary is downloaded
3. Binary is cached in an OS-specific cache directory resolved by `get_cache_dir()`, which uses `platformdirs.user_cache_dir("capiscio", "capiscio")` and stores binaries under a versioned subdirectory
4. All args are passed through to the Go binary via `subprocess`

## Quick Commands

```bash
pip install -e ".[dev]"   # Install in dev mode
pytest -v                 # Run tests
uv sync                   # Sync deps with uv
```

## Critical Rules

- **Never add CLI logic here** — all commands belong in capiscio-core
- Binary downloads use GitHub Releases from `capiscio/capiscio-core`
- Platform detection: `platform.system()` + `platform.machine()`
- The `CORE_VERSION` constant in `src/capiscio/manager.py` must track the capiscio-core release tag used for the downloaded binary; the Python package version can differ
- **Don't confuse with capiscio-sdk-python** — this is the CLI wrapper, that's the SDK

## Publishing

PyPI publish is triggered by pushing a git tag matching `v*`.
```bash
git tag v2.4.1 && git push origin v2.4.1  # Triggers PyPI publish
```
