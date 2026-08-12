# FLOOR 11 — SECURITY & BYOK AUDIT

## 1. BYOK Credential Boundary
- User API keys are stored exclusively in platform-native secure storage (Windows DPAPI vault at `.vault/`).
- Keys are never output in raw format over HTTP endpoints or written to logs.
- Masking function (`SecureKeyVault.mask_api_key`) transforms keys to `****...XXXX`.
- Key deletion immediately clears credentials from DPAPI vault.

## 2. Zero Leakage Verification
- Scanned all codebase files, manifests (`job_manifest.json`), transcripts, and render outputs: 0 raw API keys detected.
- Verified no client-side `NEXT_PUBLIC_*` credential leakage.
- Verified subprocess calls use `shell=False` with strict parameter lists.
