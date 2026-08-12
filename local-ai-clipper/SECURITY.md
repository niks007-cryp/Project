# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | ✅ Active  |

---

## Reporting a Vulnerability

**Do NOT open a public GitHub issue to report a security vulnerability.**

If you discover a security vulnerability in Local AI Clipper, please report it responsibly:

1. **Email**: Use GitHub's private vulnerability reporting feature or contact the maintainers directly via GitHub.
2. **Include**: A description of the vulnerability, steps to reproduce, and potential impact.
3. **Response time**: We aim to acknowledge reports within 72 hours and provide a resolution plan within 7 days for critical issues.

We will not take legal action against researchers who report vulnerabilities responsibly and in good faith.

---

## Credential Handling

### User BYOK Credentials

Local AI Clipper implements a strict Bring-Your-Own-Key (BYOK) policy:

- **API keys are NEVER hardcoded** in source code, configuration files, or documentation.
- **API keys are NEVER committed** to Git.
- **API keys are NEVER placed** in `NEXT_PUBLIC_*` environment variables or any client-accessible bundle.
- User credentials are stored locally on the user's machine using platform-native secure storage (DPAPI on Windows).
- The application UI receives only masked credential status (e.g., `****...1234`), not the raw key.

### What to Report

Please report if you find:
- Any API key, token, or secret accidentally committed to the repository
- Any endpoint that exposes raw credentials in its response
- Any vulnerability that allows credential extraction from the secure vault
- Any path traversal or command injection vulnerability in the media processing pipeline
- Any CORS misconfiguration that exposes the API to unauthorized origins

### What NOT to Report

The following are expected behaviors:
- The application running on `127.0.0.1` (local-only by design)
- No HTTPS on the local control panel (traffic never leaves the local machine)
- FFmpeg subprocesses (used with `shell=False` and controlled argument lists)

---

## Deployment Security

When deploying the Web Control Panel to Vercel or any cloud platform:

- **Infrastructure secrets** (deployment credentials, CI tokens) may be stored in Vercel/GitHub secret systems.
- **User BYOK credentials** must NEVER be stored in Vercel environment variables.
- **No raw API keys** should appear in server logs, error messages, or HTTP responses.
- Production error responses must not expose stack traces, filesystem paths, or internal environment variables.

---

## Dependency Security

Dependencies are audited using `pip-audit` as part of the CI pipeline. Known vulnerabilities in dependencies should be reported so they can be addressed in the next release.

---

## Responsible Disclosure

We believe in responsible disclosure. If you report a vulnerability:

1. We will work with you to understand and verify the issue.
2. We will develop a fix and release it as soon as possible.
3. We will credit you in the security advisory (unless you prefer anonymity).
4. We ask that you give us reasonable time to fix the issue before public disclosure.
