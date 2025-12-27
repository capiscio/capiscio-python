# Wrapper-Specific Commands

While most commands are handled by the Core binary, the Python wrapper includes a few utility commands for managing the wrapper itself.

## `capiscio --wrapper-version`

Displays the version of the Python wrapper package itself, distinct from the Core binary version.

```bash
$ capiscio --wrapper-version
capiscio-python wrapper v2.1.3
```

## `capiscio --wrapper-clean`

Removes the cached `capiscio-core` binary. This is useful if the binary becomes corrupted or if you want to force a re-download.

```bash
$ capiscio --wrapper-clean
Cleaned cache directory: /Users/username/Library/Caches/capiscio/bin
```

---

## Core Commands

All other commands are passed directly to the `capiscio-core` binary. See the [CLI Reference](https://docs.capisc.io/reference/cli/) for full documentation.

### Common Commands

```bash
# Validate an agent card
capiscio validate ./agent-card.json

# Validate with JSON output
capiscio validate ./agent-card.json --json

# Validate with live endpoint testing
capiscio validate https://agent.example.com --test-live

# Check version of the core binary
capiscio --version

# Generate a signing key pair
capiscio key gen --out-priv ./private.jwk --out-pub ./public.jwk
```
