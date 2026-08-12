# FLOOR 8 SECURITY SPECIFICATION — PIPELINE ORCHESTRATION

## Security Controls & Threat Mitigations

1. **Safe Process Execution:** Subprocesses constructed as explicit string argument lists via `SafeSubprocess` (`shell=False`).
2. **Path Containment:** All source media and output directory paths sanitized and validated via `validate_path_containment`.
3. **BYOK Credential Protection:** API keys stored in Windows DPAPI encrypted vault; masked in logs and manifests.
4. **Data Minimization:** External provider calls transmit only required transcript text, never full raw video files.
5. **Orphan & Temp File Cleanup:** Pipeline cancellation and failure handlers clean temporary `.tmp` files.
