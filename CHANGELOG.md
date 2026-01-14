# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.3.1] - 2025-01-14

### Changed
- **CORE VERSION**: Now downloads `capiscio-core` v2.3.1

### Fixed
- Aligned all version references across package metadata

## [2.3.0] - 2025-01-13

### Added
- **E2E Test Suite**: Comprehensive end-to-end test coverage for CLI wrapper workflows

### Fixed
- **CLI Command Syntax**: Fixed incorrect command syntax in documentation

### Changed
- **CORE VERSION**: Now downloads `capiscio-core` v2.3.0

## [2.2.0] - 2025-12-10

### Changed
- **VERSION ALIGNMENT**: All CapiscIO packages now share the same version number.
  - `capiscio-core`, `capiscio` (npm), and `capiscio` (PyPI) are all v2.2.0.
  - Simplifies compatibility - no version matrix needed.
- **CORE VERSION**: Now downloads `capiscio-core` v2.2.0.

### Added
- **Test Suite**: Added comprehensive test coverage (96%) for CLI wrapper and binary manager.

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
