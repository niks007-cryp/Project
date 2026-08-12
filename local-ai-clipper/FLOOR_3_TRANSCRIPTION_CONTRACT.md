# FLOOR 3 TRANSCRIPTION CONTRACT — LOCAL AI CLIPPER

## 1. Scope & Architectural Purpose
Floor 3 implements a production-grade local ASR transcription engine. It consumes a trusted Floor 2 `MediaAsset`, checks audio eligibility, extracts 16kHz mono PCM WAV audio (`audio_16k_mono.wav`), executes local ASR (`faster-whisper`), normalizes word-level timestamps, validates quality, records provenance, and outputs a trusted `Transcript` domain entity.

## 2. Pipeline Execution Pattern
```
MediaAsset (Floor 2)
        │
        ▼
Audio Eligibility Check (has_audio == True)
        │
        ▼
Audio Extraction / Preparation (16kHz mono PCM WAV via SafeFFmpeg)
        │
        ▼
ASR Provider Execution (FasterWhisperProvider)
        │
        ▼
Raw Transcript Result (Segments & Words)
        │
        ▼
Timestamp Normalizer (Monotonic bounds & gap alignment)
        │
        ▼
Transcript Quality Validator (Schema & temporal verification)
        │
        ▼
Provenance Recording (ASR model, device, compute_type, config_hash)
        │
        ▼
Manifest Checkpoint (jobs/<JOB_ID>/transcript/transcript.json)
```

## 3. Strict Scope Boundaries
- **IN SCOPE:** Local ASR transcription, word-level timestamps, timestamp normalization, language metadata, ASR provider abstraction, confidence scores, WER evaluation framework, CPU/GPU hardware strategy, transcript quality validation.
- **EXPLICITLY OUT OF SCOPE:** Semantic clip detection, hook scoring, candidate generation, clip ranking, LLM calls, captions, auto-reframing, video rendering.

## 4. Hardware Strategy
- **Primary:** CUDA GPU acceleration (`compute_type="float16"` or `"int8_float16"`).
- **Fallback:** CPU execution (`compute_type="int8"` or `"float32"`). Automatic fallback upon CUDA unavailability or memory failure.
- Provenance explicitly records the actual runtime device (`cuda` vs `cpu`).
