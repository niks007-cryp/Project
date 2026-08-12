# SYSTEM ARCHITECTURE — LOCAL AI CLIPPER

## 1. High-Level Modular Design
The system is constructed as a decoupled, multi-stage pipeline coordinated by a centralized Orchestrator and stateful Job Engine.

```
+-----------------------------------------------------------------------------------+
|                                   JOB ENGINE                                      |
|  +--------------------+   +---------------------+   +--------------------------+  |
|  | Ingestion Service  |-->| Audio Extractor     |-->| Transcription Engine     |  |
|  +--------------------+   +---------------------+   +--------------------------+  |
|                                                                  |                |
|  +--------------------+   +---------------------+                v                |
|  | Visual Reframer    |<--| Clip Intel Engine   |<--+--------------------------+  |
|  +--------------------+   +---------------------+   | Boundary Generator       |  |
|            |                                        +--------------------------+  |
|            v                                                                      |
|  +--------------------+   +---------------------+   +--------------------------+  |
|  | Caption Engine     |-->| FFmpeg Renderer     |-->| Quality Control (QC)     |  |
|  +--------------------+   +---------------------+   +--------------------------+  |
+-----------------------------------------------------------------------------------+
```

## 2. Core Subsystems & Interfaces

### 2.1 Ingestion Service
- **Role:** File validation, probe analysis, media hash generation, job directory initialization.
- **Contract:** Accepts raw file path -> Validates video container & codec -> Outputs `IngestionManifest`.

### 2.2 Transcription Engine (`ASRProvider`)
- **Role:** Extracts audio, runs ASR model (e.g., CTranslate2 / faster-whisper), normalizes transcript tokens.
- **Contract:** Inputs 16kHz PCM audio -> Outputs standardized `NormalizedTranscript` schema (words with exact `start_ms`, `end_ms`, `confidence`).

### 2.3 Clip Intelligence Engine (`AIProvider`)
- **Role:** Receives normalized transcript, computes boundary candidates, prompts LLM for clip scoring & hook detection, deduplicates clips.
- **Contract:** Inputs `NormalizedTranscript` -> Outputs list of `RankedClipCandidate` objects.

### 2.4 Visual Analysis & Reframing Engine
- **Role:** Tracks faces/persons per frame, computes dynamic 9:16 crop window trajectory, applies spatial smoothing filters.
- **Contract:** Inputs source video + `RankedClipCandidate` -> Outputs `CropTrajectory` curve JSON.

### 2.5 Caption Engine
- **Role:** Generates styled ASS (Advanced SubStation Alpha) subtitle files based on word timestamps and template parameters.
- **Contract:** Inputs word timestamps + `CaptionStyleSpec` -> Outputs `.ass` subtitle file.

### 2.6 Rendering & QC Engine
- **Role:** Assembles FFmpeg filtergraphs (crop + scale + captions + audio normalize), executes render, verifies output integrity.
- **Contract:** Inputs `CropTrajectory` + `.ass` file + audio/video streams -> Renders final `.mp4` clip and produces `QCReport`.

## 3. Storage & Artifact Layout
Jobs are self-contained inside dedicated directories:
```
N:/local-ai-clipper/jobs/
└── JOB_<JOB_ID>/
    ├── input/            # Raw or symlinked source media
    ├── audio/            # Extracted PCM WAV
    ├── transcript/       # Raw ASR output & NormalizedTranscript.json
    ├── candidates/       # Raw LLM responses & RankedClipCandidate.json
    ├── trajectory/       # Crop trajectory keyframes
    ├── captions/         # Generated .ass files
    ├── renders/          # Final rendered .mp4 clips
    ├── qc/               # QC logs, frame diffs, report.json
    ├── job_manifest.json # Complete state & provenance manifest
    └── logs/             # Stage execution logs
```
