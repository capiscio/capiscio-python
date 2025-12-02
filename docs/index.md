---
title: CapiscIO Python CLI - Documentation
description: Official documentation for the CapiscIO Python CLI wrapper.
---

# CapiscIO Python CLI

The **CapiscIO Python CLI** is a lightweight wrapper around the [CapiscIO Core](https://github.com/capiscio/capiscio-core) binary, designed for seamless integration into Python environments.

!!! info "This is a Wrapper Package"
    This package does NOT contain validation logic. It downloads and executes the `capiscio-core` Go binary, which performs the actual validation.

<div class="grid cards" markdown>

-   **🚀 Getting Started**

    ---

    Install the CLI via pip.

    [:octicons-arrow-right-24: Installation](./getting-started/installation.md)

-   **⚙️ Reference**

    ---

    Wrapper commands and usage.

    [:octicons-arrow-right-24: Commands](./reference/commands.md)

</div>

## Quick Start

```bash
# Install
pip install capiscio

# Validate an agent card
capiscio validate ./agent-card.json

# Validate with JSON output (includes scores)
capiscio validate ./agent-card.json --json

# Check core binary version
capiscio version
```

## What This Package Does

1. **Downloads** the correct `capiscio-core` binary for your platform (macOS/Linux/Windows, AMD64/ARM64)
2. **Caches** the binary in your user cache directory
3. **Executes** the binary with your arguments, using `os.execv()` for zero overhead

All validation logic lives in `capiscio-core`. This wrapper just makes it easy to install via pip.
