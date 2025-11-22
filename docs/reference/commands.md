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

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CAPISCIO_CORE_PATH` | (Optional) Override the path to the `capiscio-core` binary. If set, the wrapper will use this binary instead of downloading one. |
