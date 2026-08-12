# LOOP GUARDRAILS & DEVELOPMENT CONSTRAINTS — FLOOR 8

## Non-Negotiable Development Rules

1. **Database Independence:** DO NOT introduce PostgreSQL, MySQL, Redis, MongoDB, or SQLite ORM databases. Operate strictly using filesystem artifacts, atomic JSON manifests, checkpoints, and state machine transitions.
2. **BYOK Security:** User-controlled API keys must be encrypted in `SecureKeyVault`, displayed masked (`****************ABCD`), and NEVER hardcoded or logged.
3. **No Unsafe Execution:** Subprocess invocation MUST use `SafeSubprocess` (`shell=False`). No arbitrary shell commands.
4. **No Hidden Defaults:** Every model, prompt, and profile setting must be explicitly configured or come from documented project defaults.
5. **Candidate Failure Isolation:** A failure in one candidate MUST NOT invalidate successful sister candidates (`M <= N`).
6. **Mandatory Walkthrough Protocol:** Write `FLOOR_8_WALKTHROUGH.md` to disk AND print complete contents in the final response before stopping.
