# DATA FLOW & TRANSFORMATIONS — LOCAL AI CLIPPER

## 1. Primary Data Pipeline
The following graph illustrates physical file transformations and computational data flows:

```
[Raw Source Video (MP4/MKV)]
            │
            ▼ (FFmpeg Probe & Extract)
    ┌───────┴─────────────────────────┐
    │                                 │
[Extract Audio: PCM WAV 16kHz]   [Extract Video Stream Info]
    │                                 │
    ▼ (Whisper ASR Engine)            │
[Normalized Transcript (JSON)]        │
    │                                 │
    ▼ (Semantic Segmentation & LLM)   │
[Clip Candidate Intervals (JSON)]    │
    │                                 │
    ├─────────────────────────────────┘
    ▼
[Computer Vision Engine (MediaPipe/YOLO)]
    │
    ▼
[Crop Window Trajectory Array (JSON)]
    │
    ├─────────────────────────────────┐
    │                                 │
    ▼ (Caption Engine)                │
[ASS Subtitle File]                   │
    │                                 │
    └────────────────┬────────────────┘
                     ▼ (FFmpeg Filtergraph Render)
         [Rendered Vertical MP4]
                     │
                     ▼ (QC Analysis Engine)
         [QC Report & Manifest]
```

## 2. Privacy & Data Boundary Policy
- **Local Storage:** Raw video, audio streams, trajectories, and rendered clips REMAIN strictly on local storage (`N:/local-ai-clipper/jobs/...`).
- **External Transmission:** IF external LLM providers are configured (e.g. Gemini/OpenAI), ONLY text transcript snippets (`start_ms`, `end_ms`, `text`) are passed. Video binaries and frames are NEVER transmitted over the wire.
