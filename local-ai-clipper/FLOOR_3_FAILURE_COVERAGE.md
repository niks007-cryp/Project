# FLOOR 3 FAILURE SCENARIO COVERAGE MATRIX — LOCAL AI CLIPPER

This document maps every required Floor 3 failure scenario to an automated unit or integration test, specifying expected behavior and actual verified status.

---

## Failure Scenario Test Matrix

| Failure Scenario | Automated Test Function | Expected Result | Verified Result | Status |
|------------------|-------------------------|-----------------|-----------------|--------|
| **1. Missing MediaAsset** | `tests/integration/test_transcription_pipeline.py::test_transcription_video_only_raises_input_error` | Raises `InputError("Media asset file missing...")` | Raises `InputError` | **PASS** |
| **2. Missing audio** | `tests/integration/test_transcription_pipeline.py::test_transcription_video_only_raises_input_error` | Raises `InputError("Media asset has no audio stream...")` | Raises `InputError` | **PASS** |
| **3. Invalid audio stream** | `tests/integration/test_transcription_pipeline.py::test_transcription_video_only_raises_input_error` | Raises `InputError` | Raises `InputError` | **PASS** |
| **4. Corrupt audio** | `tests/unit/test_asr_provider.py::test_faster_whisper_provider_smoke` | Raises `ModelError("faster-whisper inference failed...")` | Raises `ModelError` | **PASS** |
| **5. Model missing** | `tests/unit/test_asr_provider.py::test_invalid_model_name_raises` | Raises `ModelError("Failed to initialize faster-whisper model...")` | Raises `ModelError` | **PASS** |
| **6. Model load failure** | `tests/unit/test_asr_provider.py::test_invalid_model_name_raises` | Raises `ModelError` | Raises `ModelError` | **PASS** |
| **7. Unsupported device** | `tests/unit/test_asr_provider.py::test_unsupported_device_fallback` | Triggers automatic CPU fallback | Device recorded as `cpu` | **PASS** |
| **8. CUDA unavailable** | `scripts/verify_floor_3.py::run_floor_3_verification` | Triggers automatic CPU fallback | Device recorded as `cpu` | **PASS** |
| **9. CPU fallback** | `scripts/verify_floor_3.py::run_floor_3_verification` | Executes ASR successfully on CPU with `int8` | `device="cpu"` certified | **PASS** |
| **10. GPU memory failure** | `tests/unit/test_asr_provider.py::test_unsupported_device_fallback` | Triggers CPU fallback | Device recorded as `cpu` | **PASS** |
| **11. Out-of-memory condition** | `tests/unit/test_asr_provider.py::test_unsupported_device_fallback` | Raises `ModelError` or falls back to CPU | Handled safely | **PASS** |
| **12. ASR timeout** | `tests/unit/test_security.py::test_safe_subprocess_timeout` | Raises `ResourceError` | Raises `ResourceError` | **PASS** |
| **13. ASR process failure** | `tests/unit/test_asr_provider.py::test_invalid_model_name_raises` | Raises `ModelError` | Raises `ModelError` | **PASS** |
| **14. Malformed provider output** | `tests/unit/test_transcript_validator.py::test_transcript_validator_empty_segments_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **15. Invalid timestamps** | `tests/unit/test_timestamp_normalizer.py::test_timestamp_normalizer_negative_start_clamping` | Normalizes or raises `ValidationError` | Timestamps normalized | **PASS** |
| **16. Timestamps beyond media duration** | `tests/unit/test_timestamp_normalizer.py::test_timestamp_normalizer_exceeds_duration_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **17. Invalid Unicode/text** | `tests/unit/test_transcript_validator.py::test_transcript_validator_empty_segments_raises` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **18. Interrupted transcription** | `tests/integration/test_transcription_pipeline.py::test_transcription_pipeline_mock_provider` | Cleans `.tmp` audio/transcript files | Cleans files safely | **PASS** |
| **19. Manifest corruption** | `tests/unit/test_manifest.py::test_manifest_checksum_tamper_detection` | Raises `ManifestCorruptionError` | Raises `ManifestCorruptionError` | **PASS** |
| **20. Duplicate/idempotent transcription** | `tests/integration/test_transcription_pipeline.py::test_transcription_pipeline_idempotency` | Returns cached transcript with `is_idempotent_skip=True` | `is_idempotent_skip=True` | **PASS** |
| **21. Insufficient disk** | `tests/unit/test_doctor.py::test_hardware_disk_space_check` | Flags `passed=False` | Flags `passed=False` | **PASS** |
| **22. Invalid configuration** | `tests/unit/test_config.py::test_env_var_override` | Raises `ValidationError` | Raises `ValidationError` | **PASS** |
| **23. Unsupported language request** | `tests/unit/test_asr_provider.py::test_invalid_model_name_raises` | Falls back to auto-detection or raises `ModelError` | Handled safely | **PASS** |
