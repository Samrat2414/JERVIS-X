# Changelog

## [Unreleased]

## [1.6.1] - 2026-09-01

### Added

- Added --export-settings to export JERVIS settings from the command line.
- Added --import-settings FILE with missing-path validation.

## [1.6.0] - 2026-09-01
### Added

- Added --data-path to display the active application data directory.
- Added --backup to create a local JERVIS data backup from the command line.
- Added --list-backups to display available JERVIS data backups.
- Added --latest-backup to display the newest available backup.
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