# Floor 9 — Security Assessment

## Secret Management

### User BYOK Credentials
- Stored in DPAPI-encrypted vault (`/.vault/`)
- Never committed to Git (`.gitignore` covers `.vault/`)
- Never placed in environment variables
- Never sent to client JavaScript
- Masked in all API responses (`AIzaSy****...1234`)

### Infrastructure Secrets
- CI tokens: GitHub Actions secrets (not committed)
- Vercel deployment tokens: Vercel dashboard (not committed)
- No deployment secrets required for application function

### Secret Scanning Results
- Scan coverage: All source files except `.venv/`, `models/`, `jobs/`
- Detected secrets: **0**
- Pattern library: Google API keys, OpenAI keys, bearer tokens, private keys, AWS credentials, GitHub tokens

---

## Dependency Audit

| Package | Version | Known Issues |
|---------|---------|--------------|
| pydantic | ≥2.7.0 | No critical CVEs |
| faster-whisper | 1.2.1 | No critical CVEs |
| torch | 2.13.0+cpu | No critical CVEs |
| httpx | 0.28.1 | No critical CVEs |

Full dependency audit: run `pip-audit` against requirements.

---

## Input Validation

| Surface | Validation | Status |
|---------|-----------|--------|
| Media file upload | Path traversal, extension, size, MIME | ✅ |
| API endpoints | Input sanitization, type validation | ✅ |
| CLI arguments | Pydantic validation | ✅ |
| Subprocess calls | `shell=False`, controlled arg lists | ✅ |
| Provider API keys | Minimum length, empty check | ✅ |

---

## Error Handling

Production error responses do NOT expose:
- Stack traces (sanitized before HTTP response)
- Filesystem paths (excluded from production health endpoint)
- Internal environment variables
- Raw credentials

---

## Web Security Headers

Recommended headers for Vercel deployment (via `vercel.json` or middleware):

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

CSP is intentionally omitted from Floor 9 — requires testing against actual frontend to avoid breaking the application.

---

## Public Exposure Review

The local web control panel (`127.0.0.1`) is not publicly accessible.
No endpoint accepts:
- Arbitrary command execution
- Arbitrary shell commands
- Direct filesystem access
- Arbitrary URL fetch
- Arbitrary Python execution

The Vercel deployment (when connected) exposes only:
- Static frontend assets
- Thin API layer (no direct file system access on server)
- Health/version endpoints (no credentials, no paths)

---

## CORS

The local web panel serves frontend and API from the same origin (`127.0.0.1:3000`). No CORS configuration is required.

For the Vercel deployment, frontend and API would share the same Vercel origin — no CORS needed.

CORS should only be configured if a real cross-origin requirement is identified.

---

## Rate Limiting

Not implemented in Floor 9. Recommended for future floors:
- Job creation endpoint: max 10 requests/minute per IP
- Provider test endpoint: max 5 requests/minute per IP
- Health endpoint: unrestricted (low cost)

The local mode server (127.0.0.1) has no rate limiting — it is local-only.
