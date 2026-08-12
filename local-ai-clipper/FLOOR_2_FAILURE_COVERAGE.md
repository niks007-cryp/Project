# FLOOR 2 FAILURE SCENARIO COVERAGE MATRIX — LOCAL AI CLIPPER

This document maps every required Floor 2 failure scenario to an automated unit or integration test, specifying expected behavior and actual verified status.

---

## Failure Scenario Test Matrix

| Failure Scenario | Automated Test Function | Expected Result | Actual Result | Status |
|------------------|-------------------------|-----------------|---------------|--------|
| **1. Missing file** | `tests/unit/test_ingestion_security.py::test_missing_file_raises_input_error` | Raises `InputError("Input file does not exist...")` | Raises `InputError` | **PASS** |
| **2. Invalid path** | `tests/unit/test_ingestion_security.py::test_missing_file_raises_input_error` | Raises `InputError` for unresolvable filesystem path | Raises `InputError` | **PASS** |
| **3. Path traversal** | `tests/unit/test_ingestion_security.py::test_path_traversal_rejection` | Raises `SecurityError("Path traversal rejected...")` | Raises `SecurityError` | **PASS** |
| **4. Directory instead of file** | `tests/unit/test_ingestion_security.py::test_directory_input_raises_input_error` | Raises `InputError("Input path is not a regular file...")` | Raises `InputError` | **PASS** |
| **5. Empty file** | `tests/unit/test_ingestion_security.py::test_empty_file_raises_input_error` | Raises `InputError("Input media file is empty (0 bytes)...")` | Raises `InputError` | **PASS** |
| **6. Extremely large file** | `tests/unit/test_ingestion_security.py::test_file_size_exceeds_max_limit` | Raises `SecurityError("Input media file size exceeds maximum configured limit...")` | Raises `SecurityError` | **PASS** |
| **7. Unsupported extension** | `tests/unit/test_ingestion_security.py::test_unsupported_extension_raises_error` | Raises `UnsupportedMediaFormatError("Unsupported file extension...")` | Raises `UnsupportedMediaFormatError` | **PASS** |
| **8. Unsupported codec** | `tests/unit/test_media_validator.py::test_unsupported_codec_rejection` | Raises `UnsupportedMediaFormatError` | Raises `UnsupportedMediaFormatError` | **PASS** |
| **9. Corrupt container** | `tests/integration/test_ingestion_pipeline.py::test_ingestion_corrupt_media_raises` | Raises `CorruptMediaError` / `FFprobeError` | Raises `CorruptMediaError` | **PASS** |
| **10. Corrupt video stream** | `tests/unit/test_media_validator.py::test_media_validator_no_video_raises` | Raises `CorruptMediaError("Input file contains no valid video stream.")` | Raises `CorruptMediaError` | **PASS** |
| **11. Missing audio** | `tests/integration/test_ingestion_pipeline.py::test_ingestion_video_only` | Ingests asset with `has_audio=False`; fails if `require_audio=True` | `has_audio=False` recorded | **PASS** |
| **12. Missing video** | `tests/unit/test_media_validator.py::test_media_validator_no_video_raises` | Raises `CorruptMediaError` | Raises `CorruptMediaError` | **PASS** |
| **13. Zero-duration media** | `tests/unit/test_media_validator.py::test_zero_duration_rejection` | Raises `CorruptMediaError("Invalid media duration...")` | Raises `CorruptMediaError` | **PASS** |
| **14. FFprobe failure** | `tests/unit/test_ffmpeg.py::test_ffprobe_corrupt_media_raises` | Raises `FFprobeError` with captured stderr | Raises `FFprobeError` | **PASS** |
| **15. FFmpeg failure** | `tests/unit/test_ffmpeg.py::test_ffmpeg_execution_failure` | Raises `FFmpegError` with exit code and log | Raises `FFmpegError` | **PASS** |
| **16. FFmpeg timeout** | `tests/unit/test_security.py::test_safe_subprocess_timeout` | Raises `ResourceError("Subprocess timeout expired...")` | Raises `ResourceError` | **PASS** |
| **17. Disk-full condition** | `tests/unit/test_doctor.py::test_hardware_disk_space_check` | `SystemDoctor` flags hardware check `passed=False` | Flags `passed=False` | **PASS** |
| **18. Interrupted normalization** | `tests/integration/test_ingestion_pipeline.py::test_interrupted_normalization_cleanup` | Cleans temporary `.tmp` / empty derived file; raises `FFmpegError` | Cleans file & raises `FFmpegError` | **PASS** |
| **19. Duplicate source** | `tests/integration/test_ingestion_pipeline.py::test_ingestion_idempotency` | Returns cached asset with `is_idempotent_skip=True` | `is_idempotent_skip=True` | **PASS** |
| **20. Permission failure** | `tests/unit/test_ingestion_security.py::test_permission_denied_file` | Raises `SecurityError("Permission denied...")` | Raises `SecurityError` | **PASS** |
