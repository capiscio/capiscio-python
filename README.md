# CapiscIO CLI (Python)

The official command-line interface for CapiscIO, the Agent-to-Agent (A2A) validation platform.

## Installation

```bash
pip install capiscio
```

## Usage

The CLI passes all commands directly to the underlying CapiscIO Core binary.

```bash
# Validate an agent
capiscio validate https://my-agent.example.com

# Check version
capiscio --version
```

### Wrapper Commands

The Python wrapper provides a few utility commands:

- `capiscio --wrapper-version`: Display the version of the Python wrapper.
- `capiscio --wrapper-clean`: Remove the cached `capiscio-core` binary.

## Architecture

This package is a lightweight Python wrapper around the `capiscio-core` binary (written in Go). 
When you run `capiscio`, it automatically:
1. Detects your operating system and architecture.
2. Downloads the appropriate `capiscio-core` binary release (if not already cached).
3. Executes the binary with your arguments.

Binaries are cached in your user cache directory (e.g., `~/.cache/capiscio/bin` on Linux, `~/Library/Caches/capiscio/bin` on macOS).

## License

Apache-2.0
