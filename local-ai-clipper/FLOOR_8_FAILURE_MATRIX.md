# FLOOR 8 FAILURE MATRIX — TAXONOMY & RECOVERY STRATEGY

| Failure Type | Detection Stage | Retry Policy | Recovery Action |
|--------------|-----------------|--------------|-----------------|
| **Source Corrupt / Missing** | Ingestion | No Retry | Fail job early; prompt user to inspect file. |
| **Audio Missing** | Ingestion / Transcription | No Retry | Halt audio-dependent pipeline; request valid source. |
| **ASR Provider Failure** | Transcription | Retry (max 2) | Fallback to Mock or CPU ASR provider. |
| **Candidate Scoring Error** | Clip Intelligence | Retry (max 2) | Fallback to heuristic boundary extractor. |
| **Subject Motion Track Error** | Visual Intelligence | Retry (max 2) | Fallback to static center 9:16 crop. |
| **Render Engine Failure** | Video Rendering | Retry (max 1) | Fallback from GPU to CPU `libx264` software encoder. |
| **QC Drift / Resolution Fail** | Quality Control | No Retry | Mark single candidate failed; proceed with valid candidates. |
| **Insufficient Disk Space** | Resource Planner | No Retry | Halt pipeline before FFmpeg execution; request free space. |
| **External AI Unavailable** | Provider Adapter | Retry (max 2) | Fallback to local/deterministic processing if configured. |
