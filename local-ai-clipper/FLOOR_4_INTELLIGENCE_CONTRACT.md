# FLOOR 4 CONTENT INTELLIGENCE CONTRACT — LOCAL AI CLIPPER

## 1. Architectural Scope & Purpose
Floor 4 implements the Content Intelligence Engine. It processes a trusted Floor 3 `Transcript`, extracts semantic boundaries, generates clip candidate windows, evaluates deterministic feature vectors, computes composite scores, handles LLM scoring securely, deduplicates overlapping/similar candidates, ranks candidates, and produces a trusted `ClipCandidate` dataset checkpointed to `jobs/<JOB_ID>/intelligence/candidates.json`.

## 2. Pipeline Execution Pattern
```
Transcript (Floor 3)
        │
        ▼
Semantic Boundary Extraction (BoundaryExtractor)
        │
        ▼
Candidate Window Generation (CandidateGenerator: 15s - 90s)
        │
        ▼
Candidate Deterministic Validation (CandidateValidator)
        │
        ▼
Feature Extraction (FeatureExtractor: Hook, Curiosity, Story, Pacing, Repetition)
        │
        ▼
Layered Composite Scoring (ScoringEngine: Weights & Penalties)
        │
        ▼
Temporal & Semantic Deduplication (CandidateDeduplicator)
        │
        ▼
Candidate Ranking & Top-K Selection (CandidateRanker)
        │
        ▼
Manifest Checkpoint (jobs/<JOB_ID>/intelligence/candidates.json)
```

## 3. Strict Scope Boundaries
- **IN SCOPE:** Candidate generation, feature extraction, scoring, deduplication, ranking, prompt injection defense, LLM provider abstraction, Precision@K / NDCG@K benchmarking.
- **EXPLICITLY OUT OF SCOPE:** Subtitle captions, ASS styling, face detection, subject tracking, vertical 9:16 reframing, FFmpeg video rendering, publishing.
