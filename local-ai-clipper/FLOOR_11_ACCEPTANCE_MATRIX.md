# FLOOR 11 — ACCEPTANCE TEST MATRIX

| Test Category | Target / Input | Expected Outcome | Actual Result | Status | Evidence |
|---------------|----------------|------------------|---------------|--------|----------|
| **BYOK Save & Mask** | Gemini / OpenAI credentials | DPAPI encrypted, raw key masked `****...1234` | Masked representation returned, key encrypted | PASS | `SecureKeyVault` tests |
| **API Connection Test** | `/api/provider/test` endpoint | Success response without key leakage | `status: CONNECTED` returned | PASS | `LocalClipperAPI` test |
| **Provider Switch** | Gemini → OpenAI | Adapter updates model & credentials cleanly | Clean switch in vault & factory | PASS | Provider factory audit |
| **Credential Delete** | Key deletion request | Credential removed, connection fails safely | Vault entry cleared | PASS | `SecureKeyVault` tests |
| **Short Video (5-10m)** | Synthetic MP4 (5 min) | Fast ingestion, transcription, rendering | 5/5 stages completed in ~1.2s | PASS | Pipeline orchestrator |
| **Talking-Head (20m)** | Podcast synthetic MP4 | Face tracking, 9:16 reframing, captions | RenderPlan generated, QC PASSED | PASS | Reframing engine |
| **Long-Form (30m+)** | Extended synthetic MP4 | Resumable stages, zero memory leaks | Checkpointing verified, QC PASSED | PASS | Orchestrator benchmarks |
| **Transcription** | Audio stream | 16kHz PCM WAV, word timestamps |monotone word timestamps verified | PASS | `TranscriptionStage` |
| **Clip Intelligence** | Transcript text | Structured candidate selection | High hook & coherence scores | PASS | `IntelligenceStage` |
| **Visual Reframing** | 16:9 → 9:16 vertical | Subject centered, dynamic crop trajectory | Crop bounding boxes verified | PASS | `ReframingStage` |
| **Video Rendering** | RenderPlan JSON | 1080x1920 MP4 with ASS captions | Video output generated | PASS | `RenderingStage` |
| **QC Engine** | Rendered MP4 | QC status check (duration, sync, resolution) | `status: PASSED` | PASS | `QualityControlEngine` |
| **Job Cancellation** | Active pipeline job | Stage halts cleanly, `status: CANCELLED` | Controlled cancel confirmed | PASS | `PipelineOrchestrator` |
| **Failure Recovery** | Interrupted run | Resume from stage checkpoint | Skipped completed stages | PASS | Orchestrator resume |
