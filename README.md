# CapiscIO CLI

Catch bad agents before your users do.

[![PyPI version](https://badge.fury.io/py/capiscio.svg)](https://badge.fury.io/py/capiscio)
[![Python Versions](https://img.shields.io/pypi/pyversions/capiscio.svg)](https://pypi.org/project/capiscio/)
[![License](https://img.shields.io/github/license/capiscio/capiscio-python)](https://github.com/capiscio/capiscio-python/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/capiscio)](https://pepy.tech/project/capiscio)

**CapiscIO CLI** validates A2A agent cards, tests live endpoints, and blocks broken deployments — one command in your pipeline.

> CLI secures your pipeline. [Agent Guard](https://github.com/capiscio/capiscio-sdk-python) secures your runtime.

## Installation

```bash
pip install capiscio
```

Also available via npm: `npm install -g capiscio`

## Quick Start

```bash
# Validate an agent card (local file or URL)
capiscio validate ./agent-card.json

# Validate a live agent endpoint
capiscio validate https://my-agent.example.com

# JSON output for CI pipelines
capiscio validate https://my-agent.example.com --json

# Strict mode — fail on warnings too
capiscio validate ./agent-card.json --strict
```

## What It Checks

| Check | Description |
|-------|-------------|
| **Schema** | Agent card conforms to A2A specification |
| **Signatures** | JWS badge signatures are valid |
| **Endpoints** | Live agent responds correctly (`--test-live`) |
| **Trust Level** | Badge trust level meets your threshold |

## Use Cases

- **Pre-commit hooks** — Validate agent cards before you push
- **CI/CD gates** — Block deployments with misconfigured agents ([GitHub Action](https://github.com/capiscio/validate-a2a))
- **Vendor due diligence** — Validate third-party agents before integration
- **Cron monitoring** — Continuous health checks on agent endpoints

## Dev & Testing Commands

The CLI also exposes badge and key management commands for local development and testing:

```bash
# Issue a self-signed badge (dev/testing only)
capiscio badge issue --self-sign

# Verify a badge
capiscio badge verify "$TOKEN"

# Generate a key pair
capiscio key gen

# Start the gateway sidecar
capiscio gateway start --port 8080 --target http://localhost:3000
```

For full CLI reference, see the [capiscio-core documentation](https://github.com/capiscio/capiscio-core#cli-reference).

### Wrapper Utilities

| Command | Description |
|---------|-------------|
| `capiscio --wrapper-version` | Display the version of this Python wrapper package |
| `capiscio --wrapper-clean` | Remove the cached binary (forces re-download on next run) |

## How It Works

This package is a lightweight Python wrapper around [capiscio-core](https://github.com/capiscio/capiscio-core) (written in Go). On first run it downloads the correct binary for your platform — zero overhead after that.

1. **Detects** your OS (Linux, macOS, Windows) and architecture (AMD64, ARM64)
2. **Downloads** the binary to your user cache (with SHA-256 checksum verification)
3. **Replaces** the Python process with the Go binary — native speed, no shim

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

## Related Packages

| Package | What it does | Install |
|---------|-------------|---------|
| [Agent Guard](https://github.com/capiscio/capiscio-sdk-python) | Runtime trust verification for A2A agents | `pip install capiscio-sdk` |
| [MCP Guard](https://github.com/capiscio/capiscio-mcp-python) | Trust enforcement for MCP tool servers | `pip install capiscio-mcp` |
| [capiscio-core](https://github.com/capiscio/capiscio-core) | Go library and full CLI reference | `go install` |

[Documentation](https://docs.capisc.io) · [Website](https://capisc.io) · [Platform](https://app.capisc.io)
