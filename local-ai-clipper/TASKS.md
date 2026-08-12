# FLOOR 8 ATOMIC TASK INVENTORY — END-TO-END PIPELINE & ORCHESTRATION

## Task Breakdown

- [ ] **T01 — Central Pipeline Orchestrator Core (`src/clipper/pipeline/orchestrator.py`)**
  - Implement `PipelineOrchestrator` coordinating all pipeline stages (`Ingest`, `Transcribe`, `Candidates`, `Reframing`, `Rendering`, `QC`).

- [ ] **T02 — Checkpointing & Resumability Engine**
  - Save stage checkpoints after every successful stage; support automatic resumption from last valid checkpoint upon restart.

- [ ] **T03 — Candidate Failure Isolation & Partial Success Manager**
  - Ensure individual clip candidate rendering failures do not fail valid sister candidates (`M <= N`).

- [ ] **T04 — Failure Classification & Controlled Retry Policy**
  - Implement failure taxonomy classification (`TRANSIENT`, `RESOURCE`, `VALIDATION`, `MODEL`) and enforce `max_retries` limits.

- [ ] **T05 — Pipeline Cancellation & Cleanup Engine**
  - Controlled pipeline cancellation propagating through running stages and purging temporary files.

- [ ] **T06 — Resource Governance & Local Concurrency Manager**
  - Control process execution to prevent host resource exhaustion (FFmpeg concurrency, memory footprint).

- [ ] **T07 — Provenance & Correlation Tracking**
  - Preserve `source_hash`, `pipeline_run_id`, `candidate_id`, `render_plan_hash`, `output_hash`, and model/configuration versions across all derived artifacts.

- [ ] **T08 — CLI Pipeline Subcommands (`src/clipper/cli/main.py`)**
  - Implement `clipper run <source>`, `clipper pipeline-status`, `clipper pipeline-cancel`, `clipper pipeline-retry`, `clipper pipeline-inspect`.

- [ ] **T09 — Web API Full Pipeline Endpoint (`src/clipper/web/api.py`)**
  - Expose `/api/jobs/{id}/run_full` in REST API service layer for single-click UI execution.

- [ ] **T10 — BYOK Policy Security Enforcement**
  - Verify zero hardcoded keys, DPAPI key vault integration, masked display, and zero secret leakage during orchestration.

- [ ] **T11 — Database-Independence Audit & Verification**
  - Confirm 100% database-free execution (operates using atomic manifests, checkpoints, domain models, and filesystem artifacts).

- [ ] **T12 — Floor 8 Security Specification (`FLOOR_8_SECURITY.md`)**
  - Document pipeline security bounds, input validation, command injection protection (`shell=False`), and threat mitigations.

- [ ] **T13 — Floor 8 Failure Matrix (`FLOOR_8_FAILURE_MATRIX.md`)**
  - Document failure detection, retry policy, and recovery strategy for each failure type.

- [ ] **T14 — Floor 8 Evaluation Specification (`FLOOR_8_EVALUATION.md`)**
  - Document end-to-end success rates, candidate pass rates, and pipeline quality metrics.

- [ ] **T15 — Floor 8 Performance Specification (`FLOOR_8_PERFORMANCE.md`)**
  - Document pipeline duration benchmarks, Real-Time Factor (RTF), and resource usage.

- [ ] **T16 — End-to-End Integration Test Suite (`tests/integration/test_end_to_end_pipeline.py`)**
  - Test end-to-end execution, checkpoint resumption, candidate isolation, cancellation, retry limits, and human review integration.

- [ ] **T17 — Floor 8 Gate Certification Verifier (`scripts/verify_floor_8.py`)**
  - Implement verifier testing orchestrator, checkpoint recovery, partial success, security, database independence, and Floors 1–7 regressions.

- [ ] **T18 — Execute Full Regression & Verifier Suite**
  - Run Pytest suite and Floor 1 through Floor 8 verifiers.

- [ ] **T19 — Write Floor 8 Walkthrough (`FLOOR_8_WALKTHROUGH.md`)**
  - Generate complete walkthrough document on disk.

- [ ] **T20 — Print Complete Walkthrough in Final Response & Stop**
  - Print full `FLOOR_8_WALKTHROUGH.md` directly in response and enforce absolute stop condition.
