# FLOOR 7 SECURITY SPECIFICATION — LOCAL CONTROL PLANE

## Security Controls & Threat Mitigations

1. **Local Network Containment:** Server binds to `127.0.0.1`. Remote network access disabled by default.
2. **Path Traversal Protection:** All file path arguments validated via `validate_path_containment`.
3. **Command Injection Prevention:** Subprocess invocation uses `SafeSubprocess` with explicit argument arrays (`shell=False`).
4. **BYOK Credential Vaulting:** API credentials encrypted via DPAPI/Fernet in `SecureKeyVault`.
5. **Secret Redaction:** Log viewer redacts secret patterns (`AIza`, `sk-`, `Bearer`).
6. **Input Boundary Validation:** Typed Pydantic request models sanitize all API payloads.
