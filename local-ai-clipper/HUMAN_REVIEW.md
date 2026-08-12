# HUMAN IN THE LOOP & REVIEW ARCHITECTURE — LOCAL AI CLIPPER

## 1. Principles of Human Review
1. **AI Proposes -> System Validates -> Human Decides:** Human operators have final authority to approve, reject, or adjust AI-generated clips.
2. **Reproducibility Preservation:** Human reviews MUST NOT mutate original raw AI outputs. All human interventions are stored as immutable `HumanReview` overlay records linked to specific `Clip` entities.
3. **Re-executability:** Re-running a pipeline with a saved `HumanReview` artifact deterministically reapplies the human overrides onto the pipeline outputs.

---

## 2. Supported Human Actions & Contracts

### 2.1 Approve / Reject
- **Approve:** Marks a `ClipCandidate` as `SELECTED` for rendering or publication.
- **Reject:** Marks candidate `REJECTED` with an optional rejection reason tag (`BORING`, `BAD_CUT`, `AUDIO_GLITCH`, `DUPLICATE`).

### 2.2 Timestamp Editing
- **Action:** Adjust `start_ms` and `end_ms` boundaries of a candidate clip.
- **Validation:** System deterministically validates that `modified_start_ms < modified_end_ms`, bounds remain within source media duration, and word boundaries align cleanly to transcript tokens.

### 2.3 Subtitle / Caption Tweaking
- **Action:** Override generated caption text, fix misspelled words, or alter line breaks.
- **Validation:** Re-validates subtitle text against safe zone line wrapping limits before re-generating `.ass` files.

### 2.4 Crop & Reframing Adjustment
- **Action:** Override center X trajectory keyframe offsets or select a specific speaker tracking focal point.
- **Validation:** System recalculates spatial trajectory filters and re-verifies bounding box parameters within `0 <= center_x <= source_width`.

### 2.5 Score Overriding
- **Action:** Manually set numeric hook/overall scores to promote or demote clip rank.

### 2.6 Re-rendering Trigger
- **Action:** Force re-render of a single clip with updated human parameters without invalidating transcription or segmentation checkpoints.

---

## 3. Human Review Schema (`HumanReview`)

```json
{
  "review_id": "rev_20260811_001",
  "clip_id": "clip_003",
  "reviewer_id": "editor_alex",
  "timestamp": "2026-08-11T22:45:00Z",
  "action": "EDIT_TIMESTAMPS_AND_CAPTION",
  "modifications": {
    "start_ms_delta": -1200,
    "end_ms_delta": 800,
    "caption_text_overrides": [
      { "word_id": 402, "original": "ai", "replacement": "AI" }
    ],
    "crop_center_x_offset": +40
  },
  "score_override": 95,
  "feedback_category": "PERFECT_HOOK",
  "notes": "Expanded start boundary to capture full opening question."
}
```
