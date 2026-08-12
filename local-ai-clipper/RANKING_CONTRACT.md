# CANDIDATE RANKING & DEDUPLICATION SPECIFICATION — LOCAL AI CLIPPER

## 1. Deduplication Thresholds
- **Temporal Overlap:** Candidates with temporal Intersection-over-Union (IoU) > 40% are deduplicated.
- **Semantic Overlap:** Candidates with token Jaccard text similarity > 70% are deduplicated.
- **Selection Policy:** Retains candidate with highest `composite_score`; marks lower-scoring candidate as `CandidateStatus.DUPLICATE`.

## 2. Selection & Ranking
Top-K candidates sorted by `composite_score` descending are assigned `CandidateStatus.SELECTED` and `is_selected=True`. Remaining candidates are retained with `CandidateStatus.RANKED` for provenance.
