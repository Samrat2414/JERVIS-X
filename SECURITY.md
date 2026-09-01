# Security Policy

## Supported Versions

JERVIS-X is currently under active development. Security updates are provided for the latest version.

| Version | Supported |
| ------- | --------- |
| 1.4.x   | Yes       |
| <= 1.3  | No        |

## Reporting a Vulnerability

Please do not publish sensitive security issues in a public GitHub issue.

To report a vulnerability:

1. Open the JERVIS-X repository on GitHub.
2. Go to the **Security** tab.
3. Select **Report a vulnerability**.
4. Describe the issue and steps to reproduce it.

Please do not include passwords, API keys, personal data, or other secrets.

## Credential Protection

JERVIS-X detects commands containing passwords, passcodes, API keys, secrets, tokens, and Bearer credentials.

- Sensitive values are redacted from application logs.
- Sensitive commands are blocked before conversation-history storage.
- Sensitive commands are not sent to the AI fallback.
- Users should never enter real credentials into the assistant.

## Security Recommendations

- Store API keys in a `.env` file.
- Never commit `.env` files or credentials.
- Keep dependencies updated.
- Run automated tests before each release.