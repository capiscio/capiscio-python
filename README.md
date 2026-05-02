# CapiscIO CLI (Python)

**The official command-line interface for CapiscIO, the Agent-to-Agent (A2A) validation platform.**

[![PyPI version](https://badge.fury.io/py/capiscio.svg)](https://badge.fury.io/py/capiscio)
[![Python Versions](https://img.shields.io/pypi/pyversions/capiscio.svg)](https://pypi.org/project/capiscio/)
[![License](https://img.shields.io/github/license/capiscio/capiscio-python)](https://github.com/capiscio/capiscio-python/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/capiscio)](https://pepy.tech/project/capiscio)

## Overview

This package provides a convenient Python distribution for the **CapiscIO CLI**. It acts as a smart wrapper that automatically manages the underlying `capiscio-core` binary (written in Go), ensuring you always have the correct executable for your operating system and architecture.

> **Note:** This is a wrapper. The core logic resides in [capiscio-core](https://github.com/capiscio/capiscio-core).

## Installation

```bash
pip install capiscio
```

## Usage

Once installed, the `capiscio` command is available in your terminal. It passes all arguments directly to the core binary.

```bash
# Validate an agent
capiscio validate https://my-agent.example.com

# Validate with JSON output
capiscio validate https://my-agent.example.com --json

# Check version
capiscio --version
```

### Wrapper Utilities

The Python wrapper includes specific commands to manage the binary:

| Command | Description |
|---------|-------------|
| `capiscio --wrapper-version` | Display the version of this Python wrapper package. |
| `capiscio --wrapper-clean` | Remove the cached `capiscio-core` binary (forces re-download on next run). |

## How It Works

1.  **Detection**: When you run `capiscio`, the script detects your OS (Linux, macOS, Windows) and Architecture (AMD64, ARM64).
2.  **Provisioning**: It checks if the correct `capiscio-core` binary is present in your user cache.
    *   *Linux*: `~/.cache/capiscio/bin`
    *   *macOS*: `~/Library/Caches/capiscio/bin`
    *   *Windows*: `%LOCALAPPDATA%\capiscio\bin`
3.  **Download**: If missing, it securely downloads the release from GitHub.
4.  **Execution**: It seamlessly replaces the Python process with the Go binary, ensuring zero overhead during execution.

## Supported Platforms

- **macOS**: AMD64 (Intel), ARM64 (Apple Silicon)
- **Linux**: AMD64, ARM64
- **Windows**: AMD64

## Binary Integrity Verification

On first run, the wrapper downloads the capiscio-core binary and verifies its SHA-256 checksum
against the published `checksums.txt` from the GitHub release.

Two failure modes exist:

1. **Checksum mismatch** ("Binary integrity check failed"): The downloaded file does not match
   the published checksum. This indicates tampering or corruption and **cannot be bypassed**.
   Delete the cached binary and retry.

2. **Checksums unavailable** ("checksums.txt could not be fetched" or "no entry for …"):
   The checksums file could not be downloaded or does not contain an entry for the platform
   binary. This can happen with pre-release versions or network issues. To bypass:

```bash
# Bypass only when checksums.txt is unavailable (not for mismatches)
export CAPISCIO_SKIP_CHECKSUM=true
```

## Troubleshooting

**"Permission denied" errors:**
Ensure your user has write access to the cache directory. You can reset the cache by running:
```bash
capiscio --wrapper-clean
```

**"Binary not found" or download errors:**
If you are behind a corporate firewall, ensure you can access `github.com`.

**"Binary integrity check failed":**
The downloaded binary does not match the published checksum — this may indicate a corrupted
or tampered download. Delete the cached binary (`capiscio --wrapper-clean`) and retry.
This error **cannot** be bypassed with `CAPISCIO_SKIP_CHECKSUM`.

**"Checksum verification failed: checksums.txt could not be fetched":**
The checksums file is unavailable (network issue or pre-release version). You can set
`CAPISCIO_SKIP_CHECKSUM=true` to proceed without verification, but only do this in
development environments.

## License

Apache-2.0
