# FEEDBACK ARCHITECTURE & CONTINUOUS EVALUATION LOOP — LOCAL AI CLIPPER

## 1. Architectural Concept

```
[Source Media & Transcripts] ──► [Candidate Scoring & Reframing] ──► [Human Review / Edit]
                                                                            │
                                                                            ▼ (Feedback Capture)
                                                                 [Evaluation Dataset]
                                                                            │
                                                                            ▼ (Offline Analysis)
                                                                 [Prompt / Model Tuning]
```

The system establishes data contracts to record human decisions, publish performance, and build offline benchmark datasets for continuous prompt and model optimization.

---

## 2. Data Contracts for Feedback Capture

### 2.1 Clip Evaluation Event Schema (`evaluation_event.json`)
```json
{
  "event_id": "eval_88412a",
  "job_id": "job_20260811_98412a",
  "clip_id": "clip_001",
  "ai_scores": {
    "overall": 92,
    "hook": 9.5,
    "story": 9.0
  },
  "human_action": "APPROVED_WITH_EDITS",
  "edits_summary": {
    "boundary_modified": true,
    "start_shift_ms": -800,
    "end_shift_ms": 0,
    "caption_modified": false
  },
  "performance_metrics": {
    "views_30d": 45000,
    "retention_5s_percent": 78.4,
    "completion_rate_percent": 42.1
  },
  "provenance": {
    "prompt_version_id": "prompt_hook_v1.2",
    "model_version_id": "ollama_qwen2.5_7b",
    "asr_version_id": "faster_whisper_large_v3"
  }
}
```

## 3. Ground Truth Dataset Construction
1. Every human review marked `APPROVED` or `HUMAN_EDITED` is logged into the local ground truth archive (`N:/local-ai-clipper/evaluation/ground_truth/`).
2. When prompt changes or new LLM scoring providers are evaluated in Floor 8, the system replays the evaluation dataset to measure Precision@K and Boundary Alignment Delta against human-edited ground truth.
