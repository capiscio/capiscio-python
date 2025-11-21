# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.3] - 2025-11-21

### Fixed
- **Core Version Sync**: Fixed an issue where the wrapper attempted to download a non-existent `v2.1.2` of `capiscio-core`. It now correctly downloads `v1.0.2`.
- **Package Versioning**: Bumped package version to `2.1.3` to resolve PyPI conflicts while pointing to the stable `v1.0.2` core binary.

## [2.1.2] - 2025-11-21

### Added
- **CLI Wrapper**: Initial release of the new Python CLI wrapper.
- **Architecture**: Replaced the legacy Python library with a lightweight wrapper that downloads and executes the high-performance Go binary (`capiscio-core`).
- **Platform Support**: Automatic detection and download for Linux, macOS, and Windows (AMD64/ARM64).
- **Zero Dependencies**: The wrapper itself has minimal dependencies (`rich`, `platformdirs`, `requests`) and delegates all logic to the standalone binary.

### Removed
- **Legacy Library**: Removed the old Python implementation of the validation logic in favor of the unified Go core.
