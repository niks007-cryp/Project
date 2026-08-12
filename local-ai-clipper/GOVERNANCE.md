# AI GOVERNANCE, SECURITY & COMPLIANCE — LOCAL AI CLIPPER

## 1. Governance Control Matrix

| Control Category | Control Description | Floor Introduced | Floor Enforced | Verification Test | Evidence Artifact |
|------------------|---------------------|------------------|----------------|-------------------|-------------------|
| **Data Provenance** | Track source hash, owner rights status, and media file metadata | Floor 0 | Floor 2 | `test_ingest_provenance()` | `jobs/<JOB_ID>/manifest.json` |
| **Content Rights** | Enforce user rights validation; reject unauthorized DRM media | Floor 0 | Floor 2 | `test_rights_metadata_check()` | `rights_notes` in Manifest |
| **Data Privacy** | Zero raw media transmitted externally; local ASR enforcement | Floor 0 | Floor 3 | `test_privacy_network_isolation()` | Data Policy Audit Log |
| **Model Provenance** | Log exact model names, version hashes, and provider parameters | Floor 0 | Floor 3 | `test_model_registry_logging()` | `ModelVersion` in Manifest |
| **Prompt Provenance** | Version-control LLM prompt templates and log template hashes | Floor 0 | Floor 4 | `test_prompt_version_tracking()` | `PromptVersion` in Manifest |
| **AI Boundary Enforcement** | Enforce AI Proposes -> System Validates -> System Decides | Floor 0 | Floor 4 | `test_llm_schema_validation()` | Schema Failure Logs |
| **Human Override Traceability** | Record human timestamp edits, caption changes, and score overrides | Floor 0 | Floor 5 | `test_human_review_overlay()` | `HumanReview` json file |
| **Dependency Licensing** | Audit third-party Python & binary licenses for commercial compliance | Floor 0 | Floor 1 | `test_license_compliance()` | `LICENSE_INVENTORY.md` |
| **Process Security** | Prohibit `shell=True` and string command execution; enforce array syntax | Floor 0 | Floor 1 | `test_subprocess_array_syntax()` | Security Audit Log |
| **Audit Logging** | Immutable JSON audit event log for all pipeline operations | Floor 0 | Floor 1 | `test_audit_logger()` | `pipeline_audit.log` |
| **Data Retention & Deletion**| Secure auto-purge of intermediate audio & frames | Floor 0 | Floor 10 | `test_job_cleanup()` | Purge Execution Log |

---

## 2. AI Decision Boundary Enforcement Rule
```
[ AI MODEL ] ──(Generates Proposal)──► [ SYSTEM VALIDATOR ] ──(Enforces Pydantic Schema & Bounds)──► [ SYSTEM DECIDER ]
```
- **Prohibited:** Models shall NEVER directly execute shell commands, read/write arbitrary filesystem paths, or decide if media output is valid.
- **Mandatory:** 100% of model output MUST pass deterministic schema validation.
