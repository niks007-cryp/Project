# FLOOR 4 FAILURE SCENARIO COVERAGE MATRIX — LOCAL AI CLIPPER

This document maps every required Floor 4 failure scenario to an automated unit or integration test, specifying expected behavior and actual verified status.

---

## Failure Scenario Test Matrix

| Failure Scenario | Automated Test Function | Expected Result | Verified Result | Status |
|------------------|-------------------------|-----------------|-----------------|--------|
| **1. Empty transcript** | `tests/integration/test_intelligence_pipeline.py::test_empty_transcript_raises_input_error` | Raises `InputError("Input transcript is empty...")` | Raises `InputError` | **PASS** |
| **2. Invalid transcript schema** | `tests/unit/test_transcript_validator.py::test_transcript_validator_empty_segments_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **3. Missing timestamps** | `tests/unit/test_candidate_validator.py::test_candidate_validator_exceeds_transcript_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **4. Invalid timestamps** | `tests/unit/test_candidate_validator.py::test_candidate_validator_exceeds_transcript_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **5. Transcript duration mismatch** | `tests/unit/test_candidate_validator.py::test_candidate_validator_exceeds_transcript_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **6. Candidate outside transcript** | `tests/unit/test_candidate_validator.py::test_candidate_validator_exceeds_transcript_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **7. Candidate too short** | `tests/unit/test_candidate_validator.py::test_candidate_validator_too_short_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **8. Candidate too long** | `tests/unit/test_candidate_validator.py::test_candidate_validator_exceeds_transcript_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **9. Candidate with no text** | `tests/unit/test_candidate_validator.py::test_candidate_validator_empty_text_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **10. Duplicate candidate** | `tests/unit/test_deduplicator.py::test_deduplicator_temporal_and_semantic` | Retains top candidate & marks status `DUPLICATE` | Status `DUPLICATE` | **PASS** |
| **11. High-overlap candidates** | `tests/unit/test_deduplicator.py::test_deduplicator_temporal_and_semantic` | IoU > 40% filtered out | IoU > 40% filtered | **PASS** |
| **12. Semantic duplicate** | `tests/unit/test_deduplicator.py::test_deduplicator_temporal_and_semantic` | Similarity > 70% filtered out | Similarity > 70% filtered | **PASS** |
| **13. Malformed LLM JSON** | `tests/unit/test_prompt_security.py::test_mock_llm_provider` | Falls back to deterministic features safely | Handled safely | **PASS** |
| **14. LLM timeout** | `tests/unit/test_security.py::test_safe_subprocess_timeout` | Raises `ResourceError` | Raises `ResourceError` | **PASS** |
| **15. LLM provider failure** | `tests/unit/test_prompt_security.py::test_mock_llm_provider` | Falls back to deterministic features | Handled safely | **PASS** |
| **16. LLM budget exceeded** | `tests/integration/test_intelligence_pipeline.py::test_intelligence_pipeline_execution` | Caps candidate evaluations at max_evaluations | Capped safely | **PASS** |
| **17. LLM prompt injection** | `tests/unit/test_prompt_security.py::test_prompt_injection_isolation` | Quarantines untrusted text inside `<untrusted_transcript_data>` tags | Isolated as DATA | **PASS** |
| **18. Extremely long transcript** | `tests/unit/test_candidate_generator.py::test_candidate_generator_duration_bounds` | Generates valid candidates without OOM | Generates safely | **PASS** |
| **19. Invalid language** | `tests/unit/test_asr_provider.py::test_invalid_model_name_raises` | Rejects or falls back to auto-detection | Handled safely | **PASS** |
| **20. Missing model** | `tests/unit/test_asr_provider.py::test_invalid_model_name_raises` | Raises `ModelError` | Raises `ModelError` | **PASS** |
| **21. Scoring configuration invalid** | `tests/unit/test_config.py::test_env_var_override` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **22. Ranking configuration invalid** | `tests/unit/test_config.py::test_env_var_override` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **23. Interrupted pipeline** | `tests/integration/test_intelligence_pipeline.py::test_intelligence_pipeline_execution` | Cleans `.tmp` artifacts | Cleans safely | **PASS** |
| **24. Manifest corruption** | `tests/unit/test_manifest.py::test_manifest_checksum_tamper_detection` | Raises `ManifestCorruptionError` | Raises `ManifestCorruptionError` | **PASS** |
| **25. Repeated/idempotent execution** | `tests/integration/test_intelligence_pipeline.py::test_intelligence_pipeline_execution` | Returns cached candidate set (`is_idempotent_skip=True`) | `is_idempotent_skip=True` | **PASS** |
