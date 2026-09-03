# Changelog

## [1.8.9] - 2026-09-03

### Added

- Added backup restore statistics for total, successful, failed, and rolled-back restores.
- Added restore success rate and latest restore status/time details.
- Added `--restore-statistics` CLI command.

## [1.8.8] - 2026-09-02

### Added

- Added rollback error details to backup restore history.
- Added restore history result limiting.
- Added --limit N support for the --restore-history CLI command.
## [1.8.7] - 2026-09-02

### Added

- Added backup restore history reader and human-readable history viewer.
- Added `--restore-history` CLI command to view backup recovery history.

## [1.8.6] - 2026-09-02

### Added

- Added persistent backup restore history for successful and failed recovery attempts.
- Added restore history details for safety backups, rollback status, and recovery errors.

## [1.8.5] - 2026-09-02

### Reliability

- Added automatic rollback when a backup restore operation fails.

## [Unreleased]

## [1.8.4] - 2026-09-02

### Added

- Added backup health and restore-readiness reports through CLI and JERVIS chat.
- Added automatic backup rotation with configurable `--keep N` retention policy.

## [1.8.3] - 2026-09-02

### Security

- Detect files present in a backup but missing from its SHA-256 manifest.

## [1.8.2] - 2026-09-02

### Security

- Block data restoration when backup SHA-256 integrity verification fails.

## [1.8.1] - 2026-09-02

### Added

- Added the preview restore JERVIS chat command.

## [1.8.0] - 2026-09-02

### Added

- Added `--preview-restore` for integrity-checked, read-only backup restore previews.

## [1.7.3] - 2026-09-02

### Fixed

- Made the backup chat-route regression test independent of optional desktop dependencies on Linux CI.

### Security

- Reject checksum manifest paths that escape the selected backup directory.

## [1.7.2] - 2026-09-02

### Added

- Added the verify latest backup GUI chat command.

## [1.7.1] - 2026-09-02

### Fixed

- Store packaged Windows backups under `%LOCALAPPDATA%\JERVIS-X\backups` so persistent user data is backed up correctly.

## [1.7.0] - 2026-09-02

### Security

- Added SHA-256 checksum manifests to new data backups.
- Added `--verify-latest-backup` to detect missing or modified backup files.

## [1.6.3] - 2026-09-01

### Added

- Added `--validate-settings FILE` for read-only settings validation.

## [1.6.2] - 2026-09-01

### Added

- Added `--show-settings` to display current JERVIS settings as JSON.

### Changed

- Reorganized command-line documentation into a clear reference table.

## [1.6.1] - 2026-09-01

### Added

- Added `--export-settings` to export JERVIS settings from the command line.
- Added `--import-settings FILE` with missing-path validation.

## [1.6.0] - 2026-09-01

### Added

- Added `--data-path` to display the active application data directory.
- Added `--backup` to create a local JERVIS data backup from the command line.
- Added `--list-backups` to display available JERVIS data backups.
- Added `--latest-backup` to display the newest available backup.

## [1.5.2] - 2026-09-01

### Changed

- Store packaged Windows job applications and backups permanently under `%LOCALAPPDATA%\JERVIS-X`.

## [1.5.1] - 2026-09-01

### Changed

- Store packaged Windows settings permanently under `%LOCALAPPDATA%\JERVIS-X\data`.

## [1.5.0] - 2026-09-01

### Added

- Added validated settings export and import commands.

## [1.4.3] - 2026-09-01

### Security

- Block commands containing sensitive credentials before conversation storage or AI fallback processing.

## [1.4.2] - 2026-09-01

### Security

- Redact passwords, passcodes, API keys, secrets, tokens, and Bearer credentials from command logs.

## [1.4.1] - 2026-09-01

### Changed

- Added GUI startup logging and unhandled exception capture.
- Added automatic 2 MB log rotation with three backup files.
- Store packaged Windows logs permanently under `%LOCALAPPDATA%\JERVIS-X\logs`.
- Added `--log-path` to display the active application log file.

## [1.4.0] - 2026-09-01

### Added

- Added JSON-formatted command-line diagnostics with `--diagnostics-json`.
- Added automated testing for JSON diagnostics output.

### Changed

- Improved README command-line documentation and code-block formatting.

## [1.3.3] - 2026-09-01

### Fixed

- Fixed false missing-file and missing-folder failures in packaged Windows EXE diagnostics.

## [1.3.2] - 2026-08-31

### Added

- Command-line system diagnostics option.
- Expanded automated tests for job application intelligence.

### Changed

- Increased test coverage to 75%.
- Raised minimum required coverage from 50% to 70%.

All notable changes to JERVIS-X will be documented in this file.

## [1.3.1] - 2026-08-31

### Added

- Centralized application version information
- Command-line version and help options
- Unknown command-line option validation
- Automated version and CLI tests
- Version display in the GUI title

## [1.3.0] - 2026-08-31

### Added

- Automatic Windows EXE and ZIP builds on version tags
- Automatic GitHub Release publishing
- SHA-256 checksum generation
- Node.js 24-compatible GitHub Actions

## [1.2.0] - 2026-08-31

### Added

- Ready-to-run Windows executable
- Downloadable Windows ZIP package
- Windows build PowerShell script
- Automated Windows build artifacts

## [1.1.0] - 2026-08-31

### Added

- Contribution guidelines
- Security policy
- Dependabot dependency monitoring
- GitHub issue and pull request templates
- Automated coverage reporting
- Minimum test coverage protection of 50%

### Improved

- Repository documentation and automated quality checks

## [1.0.0] - 2026-08-31

### Added

- Complete Job Application Intelligence system
- Application search, filter, sorting and detailed reports
- Application notes and status timeline
- Follow-up scheduling and reminders
- Interview scheduling, preparation and result tracking
- Job offer and joining checklist management
- Employee onboarding and career growth tracking
- CSV export and application backup support
- Automated tests with Pytest
- GitHub Actions continuous integration
- Automated test status badge
- MIT License
