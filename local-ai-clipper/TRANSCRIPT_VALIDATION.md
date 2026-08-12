# TRANSCRIPT VALIDATION & NORMALIZATION SPECIFICATION — LOCAL AI CLIPPER

## 1. Validation Rules & Assertions
Every transcript output by Floor 3 MUST pass deterministic validation assertions:

1. **Temporal Monotonicity:** Word and segment timestamps must satisfy `start_ms >= 0` and `end_ms > start_ms`.
2. **Word Ordering:** Word sequences within segments must be sorted in strictly increasing time order (`words[i].start_ms <= words[i+1].start_ms`).
3. **Segment Bound Alignment:** Segment `start_ms` must equal `words[0].start_ms` and `end_ms` must equal `words[-1].end_ms`.
4. **Media Bounds Containment:** No timestamp may exceed media duration + 500ms tolerance.
5. **Text Validity:** Segment text must be non-empty, valid UTF-8, and match word tokens.

## 2. Normalization Rules (`TimestampNormalizer`)
- Clamps minor floating point sub-millisecond deltas.
- Adjusts minor overlapping word boundaries where `words[i].end_ms > words[i+1].start_ms` by setting `words[i].end_ms = words[i+1].start_ms` if delta <= 100ms.
- Rejects fundamentally corrupted or non-monotonic timestamps (`start_ms > end_ms`).
