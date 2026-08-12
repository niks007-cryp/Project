# PROJECT SCOPE — LOCAL AI CLIPPER

## 1. Executive Summary
Local AI Clipper is a production-grade, local-first AI system designed to ingest long-form video content, perform automated speech recognition (ASR), analyze semantic hooks and narrative boundaries, execute subject-aware vertical (9:16) crop trajectories, apply animated captions, render video clips, and validate output via automated quality control (QC).

## 2. In-Scope Features (V1)
- **Ingestion & Validation:** Support MP4, MOV, MKV, WEBM containers and common codecs (H.264, HEVC, VP9, AV1, AAC, MP3, WAV). Validate media integrity before processing.
- **Audio Extraction:** High-performance FFmpeg extraction of mono 16kHz PCM audio.
- **Local Transcription:** Word-level timestamps, speaker diarization tags (where available), confidence metrics using local models (Whisper/faster-whisper).
- **Semantic Segmentation:** Boundary identification combining ASR timestamp analysis, visual scene changes, and acoustic silence markers.
- **AI Clip Intelligence:** Structured candidate generation, hook scoring, context verification, deduplication, and ranking.
- **Computer Vision & Reframing:** Face/person tracking using local CV models (MediaPipe/YOLO), crop window smoothing, safe zone compliance for 9:16 output.
- **Caption System:** Configurable typography, line wrapping, word highlighting, positioning, and burning in via FFmpeg ASS filter graphs.
- **Rendering Engine:** Hardware-accelerated (NVENC/QSV) and software fallback multi-clip export with customizable resolution and FPS.
- **Automated Quality Control (QC):** Technical checks for playability, missing audio/video, frame freezing, caption alignment, and context completeness.

## 3. Out-Of-Scope (V1 Explicit Exclusions)
- Public SaaS features, payment processing, multi-tenant billing, or subscription systems.
- Automatic social media publishing/uploading to platforms (YouTube Shorts, TikTok, Instagram Reels).
- DRM circumvention, private stream ripping, or platform restriction bypassing.
- Real-time live stream clipping.
- Mobile client development.

## 4. Architectural Boundaries
- Local execution is prioritized for all compute-heavy operations (CV, ASR, Rendering).
- External LLM providers (e.g., Gemini, OpenAI) operate purely as pluggable intelligence providers behind abstract interfaces, receiving only text transcripts and timestamps.
