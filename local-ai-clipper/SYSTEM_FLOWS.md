# SYSTEM FLOWS — LOCAL AI CLIPPER

## 1. End-to-End Processing Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as CLI / Interface
    participant JobEngine as Job Engine / Orchestrator
    participant Ingest as Ingestion Service
    participant ASR as ASR Engine
    participant Intel as Clip Intel Engine
    participant CV as CV Reframing Engine
    participant Render as FFmpeg Renderer
    participant QC as QC Engine

    User->>CLI: clipper process --input source.mp4 --style default
    CLI->>JobEngine: Initialize Job (JOB_ID)
    JobEngine->>Ingest: Ingest & Validate (source.mp4)
    Ingest-->>JobEngine: IngestionManifest (Valid)
    
    JobEngine->>Ingest: Extract Audio (16kHz PCM WAV)
    Ingest-->>JobEngine: audio.wav
    
    JobEngine->>ASR: Transcribe (audio.wav)
    ASR-->>JobEngine: NormalizedTranscript.json
    
    JobEngine->>Intel: Analyze & Score Candidates (NormalizedTranscript.json)
    Intel-->>JobEngine: RankedCandidates.json
    
    loop For each selected clip
        JobEngine->>CV: Track Subject & Calculate Trajectory (Clip Candidate)
        CV-->>JobEngine: CropTrajectory.json
        
        JobEngine->>Intel: Generate Styled ASS Captions (Word Timestamps)
        Intel-->>JobEngine: Subtitles.ass
        
        JobEngine->>Render: Execute Render (FFmpeg Filtergraph)
        Render-->>JobEngine: clip_output.mp4
        
        JobEngine->>QC: Run Automated QC (clip_output.mp4)
        QC-->>JobEngine: QCReport (PASS/FAIL)
    end
    
    JobEngine-->>CLI: Job Completed (Summary Manifest)
    CLI-->>User: Report Published Clips & Artifact Locations
```

## 2. Pipeline Error & Recovery Flow
1. **Stage Checkpointing:** Before executing any stage, the Job Engine checks `job_manifest.json` for completed stage checksums.
2. **Transient Error Retry:** If a stage fails due to a transient exception (e.g. LLM API rate limit or subprocess timeout), it retries up to 3 times using exponential backoff.
3. **Permanent Failure Isolation:** If a clip render or QC check fails for a specific clip, that clip is marked `FAILED` in the manifest without aborting the overall job.
4. **Resumption:** Rerunning `clipper retry --job JOB_ID` automatically resumes processing from the first uncompleted or failed stage.
