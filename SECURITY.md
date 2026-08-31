# Security Policy

## Supported Versions

JERVIS-X is currently under active development. Security updates are provided for the latest version.

| Version | Supported |
| ------- | --------- |
| 1.0.x   | Yes       |
| < 1.0   | No        |

## Reporting a Vulnerability

Please do not publish sensitive security issues in a public GitHub issue.

To report a vulnerability:

1. Open the JERVIS-X repository on GitHub.
2. Go to the **Security** tab.
3. Select **Report a vulnerability**.
4. Describe the issue and steps to reproduce it.

Please do not include passwords, API keys, personal data, or other secrets.

## Security Recommendations

- Store API keys in a `.env` file.
- Never commit `.env` files or credentials.
- Keep dependencies updated.
- Run automated tests before each release.