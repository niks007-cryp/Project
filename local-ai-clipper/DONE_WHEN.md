# DONE-WHEN ACCEPTANCE MATRIX — FLOOR 8 (ORCHESTRATION & PIPELINE)

Floor 8 CANNOT be certified until every item in this matrix evaluates to `[x] PASS`.

---

## 1. Orchestration & Checkpointing
- [ ] **Central Pipeline Orchestrator:** `PipelineOrchestrator` integrates all stages into a unified workflow.
- [ ] **Stage Checkpointing & Recovery:** Successful stage outputs checkpointed to manifest. Crashes resume cleanly from last valid checkpoint without reprocessing.
- [ ] **Candidate Failure Isolation:** Clip candidate rendering failures do not fail valid sister candidates (`M <= N`).
- [ ] **Retry Policy & Limits:** Controlled retries for transient errors with enforced `max_retries`.
- [ ] **Controlled Cancellation:** Job cancellation halts execution cleanly and purges temporary files.

## 2. Security, BYOK & Database Independence
- [ ] **BYOK Policy Compliance:** Enforces user-controlled API keys, DPAPI key vaulting, masked display (`****************ABCD`), and zero secret leakage.
- [ ] **Database Independence:** Operates 100% database-free using atomic manifests, checkpoints, domain models, and filesystem artifacts.
- [ ] **Command Execution Security:** Zero raw shell execution (`shell=False`). Path containment strictly enforced.

## 3. CLI & API Integration
- [ ] **CLI Commands:** `clipper run`, `clipper pipeline-status`, `clipper pipeline-cancel`, `clipper pipeline-retry`, `clipper pipeline-inspect` operational.
- [ ] **REST API Service:** `/api/jobs/{id}/run_full` triggers orchestrator execution.

## 4. Verifier & Walkthrough Protocol
- [ ] **Floor 8 Verifier:** `clipper verify-floor 8` evaluates to `[PASS] CERTIFIED COMPLETE`.
- [ ] **Full Regression Suite:** Floor 1 through Floor 8 verifiers pass 100%.
- [ ] **Mandatory Walkthrough Protocol:** `N:\local-ai-clipper\FLOOR_8_WALKTHROUGH.md` written to disk AND printed in full in final response.
