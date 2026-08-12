# PIPELINE CONTRACTS & STAGE SPECIFICATIONS — LOCAL AI CLIPPER

Every pipeline stage in Local AI Clipper follows the strict execution pattern:
`INPUT -> VALIDATE INPUT -> PROCESS -> OUTPUT -> VALIDATE OUTPUT -> CHECKPOINT`

---

## 1. Universal Stage Execution Paradigm

```
+-------------------------------------------------------------------------+
|                              STAGE RUNNER                               |
|                                                                         |
|  1. Read Inputs & Previous Stage Checkpoints                            |
|  2. Validate Inputs against Pydantic Input Schema                       |
|  3. Execute Core Stage Processing Logic (Deterministic or AI-Assisted)  |
|  4. Validate Produced Outputs against Pydantic Output Schema            |
|  5. Write Output Artifacts & Update Manifest Checkpoint Atomic File     |
+-------------------------------------------------------------------------+
```

---

## 2. Detailed Stage Contracts

### Stage 1: Ingestion & Media Validation (`stage_01_ingest`)
- **Purpose:** Ingest source file, validate container magic bytes, inspect streams via `ffprobe`, record hash and metadata.
- **Input Schema:** `IngestionInput` (`file_path: Path`, `project_id: str`).
- **Output Schema:** `IngestionManifest` (`asset_id: str`, `file_hash_sha256: str`, `duration_seconds: float`, `video_codec: str`, `audio_codec: str`, `width: int`, `height: int`, `fps: float`).
- **Input Validation:** Assert file exists, is readable, size > 1MB, format in `[mp4, mov, mkv, webm]`.
- **Output Validation:** Assert video stream and audio stream exist, duration > 10s, FPS > 0.
- **Deterministic Behavior:** Fully deterministic (`ffprobe` JSON parsing).
- **AI Involvement:** None.
- **Errors:** `ERR_FILE_NOT_FOUND`, `ERR_INVALID_CONTAINER`, `ERR_CORRUPT_MEDIA`.
- **Retry Policy:** Zero retries for missing/corrupt files.
- **Checkpoint:** Saved to `jobs/<JOB_ID>/manifest.json` under `stages.ingestion`.

---

### Stage 2: Audio Extraction (`stage_02_audio_extract`)
- **Purpose:** Extract uncompressed mono 16kHz 16-bit PCM WAV audio for local ASR consumption.
- **Input Schema:** `AudioExtractInput` (`asset_id: str`, `source_file_path: Path`).
- **Output Schema:** `AudioExtractOutput` (`audio_file_path: Path`, `audio_duration_seconds: float`, `sample_rate: int`, `channels: int`).
- **Input Validation:** Source video file exists and contains valid audio stream.
- **Output Validation:** Audio file exists, size > 0, PCM 16kHz mono format verified via `ffprobe`.
- **Deterministic Behavior:** Fully deterministic FFmpeg extraction command.
- **AI Involvement:** None.
- **Errors:** `ERR_AUDIO_STREAM_MISSING`, `ERR_FFMPEG_EXTRACTION_FAILED`.
- **Retry Policy:** 2 retries with FFmpeg parameter fallback.
- **Checkpoint:** Saved to `jobs/<JOB_ID>/audio/audio_extracted.json`.

---

### Stage 3: Local Transcription (`stage_03_transcribe`)
- **Purpose:** Run local ASR model (`faster-whisper`), generate word-level aligned timestamps and confidence scores.
- **Input Schema:** `TranscribeInput` (`audio_file_path: Path`, `language: Optional[str]`, `model_name: str`).
- **Output Schema:** `NormalizedTranscript` (`language: str`, `segments: List[TranscriptSegment]`, `words: List[TranscriptWord]`).
- **Input Validation:** Audio PCM file exists and is readable.
- **Output Validation:** Word timestamps strictly monotonic (`start_ms < end_ms`), words non-empty, confidence in `[0.0, 1.0]`.
- **Deterministic Behavior:** Deterministic decoding with `temperature=0.0`.
- **AI Involvement:** Local ASR Model (`faster-whisper-large-v3`).
- **Errors:** `ERR_ASR_MODEL_LOAD_FAILED`, `ERR_CUDA_OOM`, `ERR_EMPTY_TRANSCRIPT`.
- **Retry Policy:** Retry 1 with CPU fallback if CUDA OOM occurs.
- **Checkpoint:** Saved to `jobs/<JOB_ID>/transcript/transcript.json`.

---

### Stage 4: Semantic Segmentation & Candidate Generation (`stage_04_candidate_gen`)
- **Purpose:** Identify coherent candidate clip intervals (15s to 90s target duration) using ASR timestamps, silence gaps, and punctuation boundaries.
- **Input Schema:** `CandidateGenInput` (`transcript: NormalizedTranscript`, `min_duration_sec: float`, `max_duration_sec: float`).
- **Output Schema:** `CandidateGenOutput` (`candidates: List[ClipCandidate]`).
- **Input Validation:** Valid `NormalizedTranscript` with >= 10 words.
- **Output Validation:** Candidate bounds within total video duration; no candidate < 10s or > 120s.
- **Deterministic Behavior:** Fully deterministic rule-based boundary detection algorithm.
- **AI Involvement:** None (Rule-based candidate generation).
- **Errors:** `ERR_NO_CANDIDATES_GENERATED`.
- **Retry Policy:** Retry with expanded duration bounds.
- **Checkpoint:** Saved to `jobs/<JOB_ID>/candidates/raw_candidates.json`.

---

### Stage 5: Clip Scoring & Ranking (`stage_05_clip_score`)
- **Purpose:** Prompt LLM scoring model to evaluate candidates for hook strength, story arc, curiosity, and emotional resonance.
- **Input Schema:** `ClipScoreInput` (`candidates: List[ClipCandidate]`, `transcript_context: str`, `provider_config: AIProviderConfig`).
- **Output Schema:** `ClipScoreOutput` (`scored_candidates: List[ClipScore]`).
- **Input Validation:** Candidates list non-empty; prompt version verified.
- **Output Validation:** Pydantic schema validation of structured JSON response; scores bounded 0-100; confidence in `[0.0, 1.0]`.
- **Deterministic Behavior:** AI-assisted scoring with strict temperature control (`0.2`) and schema enforcement.
- **AI Involvement:** `AIProvider` (Local Ollama / Gemini / OpenAI).
- **Errors:** `ERR_LLM_PROVIDER_UNAVAILABLE`, `ERR_LLM_SCHEMA_VALIDATION_FAILED`, `ERR_RATE_LIMIT`.
- **Retry Policy:** Up to 3 retries with exponential backoff; fallback to rule-based heuristic scoring if LLM fails repeatedly.
- **Checkpoint:** Saved to `jobs/<JOB_ID>/candidates/scored_candidates.json`.

---

### Stage 6: Visual Analysis & Reframing (`stage_06_reframe`)
- **Purpose:** Detect speaker faces/subjects per frame using MediaPipe, compute dynamic 9:16 vertical crop window keyframes, apply spatial smoothing.
- **Input Schema:** `ReframeInput` (`source_video_path: Path`, `clip: ClipCandidate`, `target_aspect_ratio: str = "9:16"`).
- **Output Schema:** `CropTrajectory` (`clip_id: str`, `keyframes: List[TrajectoryKeyframe]`, `smoothing_applied: bool`).
- **Input Validation:** Source video playable; clip interval within media bounds.
- **Output Validation:** Crop window coordinates strictly inside source resolution (`0 <= center_x <= source_width`).
- **Deterministic Behavior:** Deterministic CV tracking & moving-average spatial filter math.
- **AI Involvement:** Computer Vision Model (MediaPipe Face/Pose).
- **Errors:** `ERR_VISION_MODEL_FAILED`, `ERR_NO_SUBJECT_DETECTED`.
- **Retry Policy:** Fallback to static center-crop trajectory if face tracking fails.
- **Checkpoint:** Saved to `jobs/<JOB_ID>/trajectory/trajectory_<CLIP_ID>.json`.

---

### Stage 7: Caption Styling & Burn-in (`stage_07_captions`)
- **Purpose:** Convert word timestamps into timed ASS subtitle files with custom styling templates and enforced safe zones.
- **Input Schema:** `CaptionGenInput` (`words: List[TranscriptWord]`, `style: CaptionStyle`).
- **Output Schema:** `CaptionGenOutput` (`ass_file_path: Path`, `line_count: int`).
- **Input Validation:** Word array non-empty; caption style parameters valid.
- **Output Validation:** ASS file exists, syntax valid, no line overflows past 9:16 safe zone bounds.
- **Deterministic Behavior:** Fully deterministic subtitle generation math.
- **AI Involvement:** None.
- **Errors:** `ERR_ASS_SYNTAX_ERROR`, `ERR_SAFE_ZONE_OVERFLOW`.
- **Retry Policy:** 1 retry with auto-wrapping font size reduction.
- **Checkpoint:** Saved to `jobs/<JOB_ID>/captions/captions_<CLIP_ID>.ass`.

---

### Stage 8: FFmpeg Video Rendering (`stage_08_render`)
- **Purpose:** Assemble FFmpeg filtergraph (crop + scale + ASS subtitles + audio re-encoding), execute render output clip.
- **Input Schema:** `RenderInput` (`source_video_path: Path`, `trajectory: CropTrajectory`, `ass_file_path: Path`, `output_preset: str`).
- **Output Schema:** `RenderOutput` (`rendered_clip_path: Path`, `render_duration_ms: int`, `file_size_bytes: int`).
- **Input Validation:** Inputs exist; trajectory keyframes valid.
- **Output Validation:** Rendered `.mp4` file exists, size > 500KB, resolution = 1080x1920.
- **Deterministic Behavior:** Deterministic FFmpeg encoding pipeline.
- **AI Involvement:** None.
- **Errors:** `ERR_FFMPEG_RENDER_FAILED`, `ERR_DISK_FULL`.
- **Retry Policy:** Retry 1 with software encoder (`libx264`) if NVENC fails.
- **Checkpoint:** Saved to `jobs/<JOB_ID>/renders/clip_<CLIP_ID>.mp4`.

---

### Stage 9: Automated Quality Control (`stage_09_qc`)
- **Purpose:** Run automated post-render verification assertions on the final output MP4.
- **Input Schema:** `QCInput` (`rendered_clip_path: Path`, `expected_duration_seconds: float`).
- **Output Schema:** `QCResult` (`status: QCStatus`, `playable: bool`, `audio_sync_drift_ms: float`, `frozen_frames: int`, `black_frames: int`).
- **Input Validation:** Rendered file path provided.
- **Output Validation:** All QC assertions evaluated (`PASSED` / `FAILED`).
- **Deterministic Behavior:** Fully deterministic `ffprobe` and frame diff metrics.
- **AI Involvement:** None.
- **Errors:** `ERR_QC_CHECK_FAILED`.
- **Retry Policy:** Flag clip for human review or re-render.
- **Checkpoint:** Saved to `jobs/<JOB_ID>/qc/qc_<CLIP_ID>.json`.
